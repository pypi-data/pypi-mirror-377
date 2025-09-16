# SPDX-License-Identifier: MIT
"""Generic timed event handler for time trial and pursuit track events."""

# Refer: UCI Regulations Part 3 "Track Races" 3.2.051 - 3.2.075
#        and 3.2.101 - 3.2.112

import os
import gi
import logging

gi.require_version("GLib", "2.0")
from gi.repository import GLib

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

import metarace
from metarace import tod
from metarace import strops
from metarace import report
from metarace import jsonconfig
from math import ceil

from . import uiutil
from . import scbwin

# temporary
from functools import cmp_to_key

_log = logging.getLogger('ittt')
_log.setLevel(logging.DEBUG)

# config version string
EVENT_ID = 'ittt-2.1'

# event model columns
COL_NO = 0
COL_NAME = 1
COL_MEMBERS = 3
COL_COMMENT = 4
COL_SEED = 5
COL_PLACE = 6
COL_START = 7
COL_FINISH = 8
COL_LASTLAP = 9
COL_SPLITS = 10
_VIEWCOL_MEMBERS = 2  # Team member list col

# scb function key mappings
key_reannounce = 'F4'  # (+CTRL) calls into delayed announce
key_startlist = 'F6'  # re-display running time (startlist)
key_results = 'F4'  # recalc/show result window

# timing function key mappings
key_armstart = 'F5'  # arm for start impulse
key_armlap_A = 'F7'  # arm for lap 'Front'
key_armlap_B = 'F8'  # arm for lap 'Back'
key_armfinish_A = 'F9'  # arm for finish impulse 'Front'
key_armfinish_B = 'F10'  # arm for finish impulse 'Back'
key_catch_A = 'F11'  # A rider catches B
key_catch_B = 'F12'  # B rider catches A

# extended function key mappings
key_abort = 'F5'  # + ctrl for clear/abort
key_falsestart = 'F6'  # + ctrl for false start
key_abort_A = 'F7'  # + ctrl abort A
key_abort_B = 'F8'  # + ctrl abort B


# temporary
def cmp(x, y):
    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return 0


class ittt:

    def ridercb(self, rider):
        """Rider change notification"""
        if self.winopen:
            if rider is not None:
                rno = rider[0]
                series = rider[1]
                if series == self.series:
                    dbr = self.meet.rdb[rider]
                    rh = self._getrider(rno)
                    if rh is not None:
                        _log.debug('Rider change notify: %r', rider)
                        rh[COL_NAME] = dbr.listname()
                        if not rh[COL_MEMBERS]:
                            rh[COL_MEMBERS] = dbr['members']
            else:
                # riders db changed, handled by meet object
                pass

    def eventcb(self, event):
        """Event change notification function"""
        if self.winopen:
            if event is None or event == self.evno:
                if self.prefix_ent.get_text() != self.event['pref']:
                    self.prefix_ent.set_text(self.event['pref'])
                if self.info_ent.get_text() != self.event['info']:
                    self.info_ent.set_text(self.event['info'])
                # re-draw summary line
                self.update_expander_lbl_cb()

    def standingstr(self):
        return self._standingstr

    def key_event(self, widget, event):
        """Race window key press handler."""
        if event.type == Gdk.EventType.KEY_PRESS:
            key = Gdk.keyval_name(event.keyval) or 'None'
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                if key == key_abort:  # override ctrl+f5
                    self.toidle()
                    return True
                elif key == key_reannounce:  # run delayed announce
                    GLib.idle_add(self.delayed_announce)
                    return True
                elif key == key_falsestart:  # false start both lanes
                    self.falsestart()
                    return True
                elif key == key_abort_A:  # abort front straight rider
                    self.abortrider(self.fs)
                    return True
                elif key == key_abort_B:
                    self.abortrider(self.bs)
                    return True
            elif key[0] == 'F':
                if key == key_armstart:
                    self.armstart()
                    return True
                elif key == key_armlap_A:
                    self.armlap(self.fs, self.chan_A)
                    return True
                elif key == key_armlap_B:
                    self.armlap(self.bs, self.chan_B)
                    return True
                elif key == key_armfinish_A:
                    self.armfinish(self.fs, self.chan_A)
                    return True
                elif key == key_armfinish_B:
                    self.armfinish(self.bs, self.chan_B)
                    return True
                elif key == key_catch_A:
                    self.catchrider(self.fs)
                    return True
                elif key == key_catch_B:
                    self.catchrider(self.bs)
                    return True
                elif key == key_startlist:
                    self.showtimerwin()
                    return True
                elif key == key_results:
                    self.do_places()
                    return True
        return False

    def do_places(self):
        """Show race result on scoreboard."""
        self.meet.scbwin = None
        self.timerwin = False  # TODO: bib width enhancement
        fmtplaces = []
        name_w = self.meet.scb.linelen - 12
        fmt = ((3, 'l'), (3, 'r'), ' ', (name_w, 'l'), (5, 'r'))
        if self.teamnames:
            name_w = self.meet.scb.linelen - 9
            fmt = ((3, 'l'), ' ', (name_w, 'l'), (5, 'r'))
        rcount = 0
        pcount = 0
        for r in self.riders:
            rcount += 1
            if r[COL_PLACE] is not None and r[COL_PLACE] != '':
                pcount += 1
                plstr = r[COL_PLACE]
                if plstr.isdigit():
                    plstr = plstr + '.'
                name, club = self._getname(r[COL_NO], width=name_w)
                if len(club) != 3:
                    club = ''
                if not self.teamnames:
                    bib = r[COL_NO]
                    fmtplaces.append((plstr, bib, name, club))
                else:
                    fmtplaces.append((plstr, name, club))
        evtstatus = 'Standings'
        if rcount > 0 and pcount == rcount:
            evtstatus = 'Result'

        self.meet.scbwin = scbwin.scbtable(scb=self.meet.scb,
                                           head=self.meet.racenamecat(
                                               self.event),
                                           subhead=evtstatus.upper(),
                                           coldesc=fmt,
                                           rows=fmtplaces)
        self.meet.scbwin.reset()

    def todstr(self, col, cr, model, iter, data=None):
        """Format tod into text for listview."""
        ft = model.get_value(iter, COL_FINISH)
        if ft is not None:
            sp = model.get_value(iter, COL_LASTLAP)
            st = model.get_value(iter, COL_START)
            if st is None:
                st = tod.ZERO
            mstr = (ft - st).rawtime(self.precision)
            sstr = ''
            if sp is not None:
                sstr = '/' + (ft - sp).rawtime(self.precision)
            cr.set_property('text', mstr + sstr)
        else:
            cr.set_property('text', '')

    def setup_splits(self):
        """Prepare split data for the event based on distance."""
        track_n = None
        track_d = None
        track_l = None
        event_d = None
        self.splitlist = []
        self.splitmap = {}
        try:
            # note: this partially replicates get_distance from trackmeet
            track_n = float(self.meet.tracklen_n)
            track_d = float(self.meet.tracklen_d)
            track_l = track_n / track_d
            if self.units in ('metres', 'meters'):
                event_d = float(self.distance)
            elif self.units == 'laps':
                event_d = track_n * float(self.distance) / track_d
        except Exception as e:
            _log.warning('Unable to setup splits: %s', e)
        if event_d is not None and track_l is not None:
            _log.debug('Track lap=%0.1f, Event dist=%0.1f', track_l, event_d)
            # add a dummy entry for the finish passing
            splitid = '{0:0.0f}m'.format(event_d)
            self.splitlist.insert(0, splitid)
            # work backward from finish by half-laps, adding data holders
            count = 1
            while True:
                splitdist = event_d - (count * 0.5 * track_n / track_d)
                if splitdist > 15.0:  # token minimum first inter
                    splitid = '{0:0.0f}m'.format(splitdist)
                    self.splitlist.insert(0, splitid)
                    self.splitmap[splitid] = {
                        'dist': splitdist,
                        'data': tod.todlist(splitid),
                    }
                else:
                    break
                count += 1
            _log.debug('Configured %r splits: %r', len(self.splitlist),
                       self.splitlist)
            if self.winopen:
                self.fs.splitlbls = self.splitlist
                self.bs.splitlbls = self.splitlist
        else:
            _log.debug('Splits not available')

    def loadconfig(self):
        """Load race config from disk."""
        self.riders.clear()
        self.results.clear()

        # defaults: dual timer, C0 start, PA/PB
        deftimetype = 'dual'
        defdistance = ''
        defdistunits = 'metres'
        defprecision = 3
        defchans = 0
        defchana = 2
        defchanb = 3
        defautotime = False  # without splits, this is not reliable
        self.seedsrc = 1  # fetch seed from the rank col

        # type specific overrides
        if 'race' in self.evtype:
            self.difftime = True

        self.teampursuit = False
        if 'team' in self.evtype or self.series.startswith('t'):
            self.teamnames = True
            if 'pursuit' in self.evtype:
                self.teampursuit = True
                defprecision = 2

        cr = jsonconfig.config({
            'event': {
                'startlist': '',
                'id': EVENT_ID,
                'start': None,
                'lstart': None,
                'fsbib': None,
                'fsstat': 'idle',
                'bsbib': None,
                'bsstat': 'idle',
                'showinfo': False,
                'showcats': False,
                'decisions': [],
                'distance': defdistance,
                'distunits': defdistunits,
                'precision': defprecision,
                'chan_S': defchans,
                'chan_A': defchana,
                'chan_B': defchanb,
                'autotime': defautotime,
                'inomnium': False,
                'timetype': deftimetype,
            }
        })
        cr.add_section('event')
        cr.add_section('riders')
        cr.add_section('splits')
        cr.add_section('traces')
        if not cr.load(self.configfile):
            _log.info('%r not read, loading defaults', self.configfile)

        self.chan_S = strops.confopt_chan(cr.get('event', 'chan_S'), defchans)
        self.chan_A = strops.confopt_chan(cr.get('event', 'chan_A'), defchana)
        self.chan_B = strops.confopt_chan(cr.get('event', 'chan_B'), defchanb)
        self.decisions = cr.get('event', 'decisions')
        self.distance = strops.confopt_dist(cr.get('event', 'distance'))
        self.units = strops.confopt_distunits(cr.get('event', 'distunits'))
        # override event configuration from program entry
        if self.event['laps']:
            self.units = 'laps'
            self.distance = strops.confopt_posint(self.event['laps'],
                                                  self.distance)
            _log.debug('Event distance set by program entry: %r laps',
                       self.distance)

        self.set_timetype(cr.get('event', 'timetype'))
        self.autotime = strops.confopt_bool(cr.get('event', 'autotime'))
        self.showcats = cr.get_bool('event', 'showcats')
        self.inomnium = strops.confopt_bool(cr.get('event', 'inomnium'))
        if self.inomnium:
            self.seedsrc = 3  # read seeding from points standing
        self.precision = strops.confopt_posint(cr.get('event', 'precision'), 3)

        # re-initialise split data
        self.setup_splits()

        # re-load starters and results
        self.onestart = False
        rlist = cr.get('event', 'startlist').upper().split()
        for r in rlist:
            nr = [r, '', '', '', '', '', '', None, None, None, None]
            co = ''
            st = None
            ft = None
            lt = None
            sp = {}
            if cr.has_option('riders', r):
                ril = cr.get('riders', r)
                if len(ril) >= 1:  # save comment for stimes
                    co = ril[0]
                if len(ril) >= 2:  # write heat into rec
                    nr[COL_SEED] = ril[1]
                if len(ril) >= 3:  # write heat into rec
                    nr[COL_MEMBERS] = ril[2]
                if len(ril) >= 4:  # Start ToD and others
                    st = tod.mktod(ril[3])
                    if st is not None:
                        self.onestart = True
                if len(ril) >= 5:  # Finish ToD
                    ft = tod.mktod(ril[4])
                if len(ril) >= 6:  # start of last lap ToD
                    lt = tod.mktod(ril[5])
            dbr = self.meet.rdb.get_rider(r, self.series)
            if dbr is not None:
                nr[COL_NAME] = dbr.listname()
                if not nr[COL_MEMBERS]:
                    # pull in members from riderdb if not yet defined
                    nr[COL_MEMBERS] = dbr['members']
            nri = self.riders.append(nr)
            if not self.readonly:
                # skip fetching traces and split if opened readonly
                if cr.has_option('traces', r):
                    self.traces[r] = cr.get('traces', r)
                if cr.has_option('splits', r):
                    rsplit = cr.get('splits', r)
                    for sid, split in rsplit.items():
                        sp[sid] = tod.mktod(split)
            self.settimes(nri, st, ft, lt, sp, doplaces=False, comment=co)
        self.placexfer()

        if not self.onestart and self.event['auto']:
            self.riders.clear()
            self.meet.autostart_riders(self,
                                       self.event['auto'],
                                       infocol=self.seedsrc)

        if self.winopen:
            if self.teamnames:
                self.view.get_column(_VIEWCOL_MEMBERS).set_visible(True)
            self.fs.precision = self.precision
            self.bs.precision = self.precision
            self.update_expander_lbl_cb()
            self.info_expand.set_expanded(
                strops.confopt_bool(cr.get('event', 'showinfo')))

            # re-join any existing timer state
            curstart = tod.mktod(cr.get('event', 'start'))
            lstart = tod.mktod(cr.get('event', 'lstart'))
            if lstart is None:
                lstart = curstart  # can still be None if start not set
            dorejoin = False

            # Front straight
            fsstat = cr.get('event', 'fsstat')
            if fsstat in ('running',
                          'load'):  # running with no start gets load
                self.fs.setrider(cr.get('event', 'fsbib'))  # will set 'load'
                if fsstat == 'running' and curstart is not None:
                    self.fs.start(curstart)  # overrides to 'running'
                    dorejoin = True

            # Back straight
            bsstat = cr.get('event', 'bsstat')
            if bsstat in ('running',
                          'load'):  # running with no start gets load
                self.bs.setrider(cr.get('event', 'bsbib'))  # will set 'load'
                if bsstat == 'running' and curstart is not None:
                    self.bs.start(curstart)  # overrides to 'running'
                    dorejoin = True

            if dorejoin:
                self.torunning(curstart, lstart)
            elif self.timerstat == 'idle':
                GLib.idle_add(self.fs.grab_focus)
        else:
            # cache showinfo, start, lstart, Xsstat and Xsbib
            for key in (
                    'lstart',
                    'start',
                    'fsstat',
                    'fsbib',
                    'bsstat',
                    'bsbib',
                    'showinfo',
            ):
                self._winState[key] = cr.get('event', key)

        # After load complete - check config and report.
        eid = cr.get('event', 'id')
        if eid and eid != EVENT_ID:
            _log.info('Event config mismatch: %r != %r', eid, EVENT_ID)

    def saveconfig(self):
        """Save race to disk."""
        if self.readonly:
            _log.error('Attempt to save readonly event')
            return
        cw = jsonconfig.config()
        cw.add_section('event')

        # save basic race properties
        cw.set('event', 'distance', self.distance)
        cw.set('event', 'distunits', self.units)
        cw.set('event', 'chan_S', self.chan_S)
        cw.set('event', 'chan_A', self.chan_A)
        cw.set('event', 'chan_B', self.chan_B)
        cw.set('event', 'timetype', self.timetype)
        cw.set('event', 'autotime', self.autotime)
        cw.set('event', 'startlist', self.get_startlist())
        cw.set('event', 'inomnium', self.inomnium)
        cw.set('event', 'showcats', self.showcats)
        cw.set('event', 'precision', self.precision)
        cw.set('event', 'decisions', self.decisions)

        if self.winopen:
            cw.set('event', 'showinfo', self.info_expand.get_expanded())
            cw.set('event', 'fsstat', self.fs.getstatus())
            cw.set('event', 'fsbib', self.fs.getrider())
            cw.set('event', 'bsstat', self.bs.getstatus())
            cw.set('event', 'bsbib', self.bs.getrider())
            cw.set('event', 'start', self.curstart)
            cw.set('event', 'lstart', self.lstart)
        else:
            for key in (
                    'lstart',
                    'start',
                    'fsstat',
                    'fsbib',
                    'bsstat',
                    'bsbib',
                    'showinfo',
            ):
                cw.set('event', key, self._winState[key])

        cw.add_section('riders')
        cw.add_section('traces')
        cw.add_section('splits')

        # save out all starters
        for r in self.riders:
            rno = r[COL_NO]
            slice = [r[COL_COMMENT], r[COL_SEED], r[COL_MEMBERS]]
            tl = [r[COL_START], r[COL_FINISH], r[COL_LASTLAP]]
            for t in tl:
                if t is not None:
                    slice.append(t.rawtime())
                else:
                    slice.append(None)
            cw.set('riders', rno, slice)

            # save timing traces
            if rno in self.traces:
                cw.set('traces', rno, self.traces[rno])

            # save split times
            if r[COL_SPLITS]:
                rs = {}
                for sp in r[COL_SPLITS]:
                    if r[COL_SPLITS][sp] is not None:
                        st = r[COL_SPLITS][sp].rawtime()
                        rs[sp] = st
                cw.set('splits', rno, rs)

        cw.set('event', 'id', EVENT_ID)
        _log.debug('Saving event config %r', self.configfile)
        with metarace.savefile(self.configfile) as f:
            cw.write(f)

    def startlist_report(self, program=False):
        """Return a startlist report."""
        ret = []
        cnt = 0
        secid = 'ev-' + str(self.evno).translate(strops.WEBFILE_UTRANS)
        sec = report.dual_ittt_startlist(secid)
        sec.nobreak = True
        sec.showheats = True
        if self.timetype == 'single':
            sec.set_single()
            if self.teamnames and self.series != 'tmsl':
                # TMSL is for madison support events
                sec.showheats = True

        headvec = self.event.get_info(showevno=True).split()
        if not program:
            headvec.append('- Start List')
        sec.heading = ' '.join(headvec)

        lapstring = strops.lapstring(self.event['laps'])
        substr = ' '.join((
            lapstring,
            self.event['distance'],
            self.event['phase'],
        )).strip()
        if substr:
            sec.subheading = substr
        if self.event['reco']:
            sec.footer = self.event['reco']
        if self.event['plac']:
            sec.lines = self.get_heats(placeholders=self.event['plac'])
        else:
            sec.lines = self.get_heats()
        ret.append(sec)
        return ret

    def sort_startlist(self, x, y):
        """Comparison function for ttt seeding."""
        if x[1] == y[1]:  # same seed? revert to bib ascending
            return cmp(x[2], y[2])
        else:
            return cmp(x[1], y[1])

    def sort_heats(self, x, y):
        """Comparison function for ttt heats."""
        (xh, xl) = strops.heatsplit(x[0])
        (yh, yl) = strops.heatsplit(y[0])
        if xh == yh:
            return cmp(xl, yl)
        else:
            return cmp(xh, yh)

    def reorder_startlist(self):
        """Reorder model according to the seeding field."""
        if len(self.riders) > 1:
            auxmap = []
            cnt = 0
            for r in self.riders:
                auxmap.append([
                    cnt,
                    strops.riderno_key(r[COL_SEED]),
                    strops.riderno_key(r[COL_NO])
                ])
                cnt += 1
            auxmap.sort(key=cmp_to_key(self.sort_startlist))
            self.riders.reorder([a[0] for a in auxmap])

    def get_heats(self, placeholders=0, cats=None):
        """Return a list of heats in the event."""
        ret = []

        # arrange riders by seeding
        self.reorder_startlist()

        # then build aux map of heats
        hlist = []
        emptyrows = False
        count = len(self.riders)
        if count < placeholders:
            count = placeholders
            miss = 2000
            while len(self.riders) < count:
                self.addrider(str(miss))  # WARNING!
                miss += 1
        blanknames = False
        if placeholders > 0:
            blanknames = True
        if self.timetype == 'single':
            for r in self.riders:
                rno = r[COL_NO]
                info = None
                if cats and rno in cats:
                    info = cats[rno]
                rh = self.meet.rdb.get_rider(rno, self.series)
                rname = ''
                heat = str(count) + '.1'
                if rh is not None:
                    rname = rh.resname()
                    if self.teamnames:
                        # todo: remove madison teams from ittt
                        info = []
                        col = 'black'
                        for member in r[COL_MEMBERS].split():
                            trh = self.meet.rdb.fetch_bibstr(member)
                            if trh is not None:
                                trno = trh['no']
                                if self.series == 'tmsl':  # TODO: remove
                                    trno = col
                                    col = 'red'
                                info.append([trno, trh.resname(), None])
                    # TODO: fix tandem labels
                    if rh.in_cat('tandem') and rh['note']:
                        ph = self.meet.rdb.get_rider(rh['note'], self.series)
                        if ph is not None:
                            info = [[
                                ' ',
                                ph.resname() + ' - Pilot', ph['uciid']
                            ]]
                if self.teamnames:  # Team no hack
                    rno = ' '  # force name
                hlist.append([heat, rno, rname, info])
                # all heats are one up
                count -= 1
        else:
            hno = int(ceil(0.5 * count))
            lane = 1
            for r in self.riders:
                rno = r[COL_NO]
                rh = self.meet.rdb.get_rider(rno, self.series)
                rname = ''
                heat = str(hno) + '.' + str(lane)
                info = None
                if cats and rno in cats:
                    info = cats[rno]
                if rh is not None:
                    rname = rh.resname()
                    if self.teamnames:
                        # todo: remove madison teams from ittt
                        info = []
                        col = 'black'
                        for member in r[COL_MEMBERS].split():
                            trh = self.meet.rdb.fetch_bibstr(member)
                            if trh is not None:
                                trno = trh['no']
                                if self.series == 'tmsl':  # TODO: remove
                                    trno = col
                                    col = 'red'
                                info.append([trno, trh.resname(), None])
                    # TODO: fix tandem labels
                    if rh.in_cat('tandem') and rh['note']:
                        ph = self.meet.rdb.get_rider(rh['note'], self.series)
                        if ph is not None:
                            info = [[
                                ' ',
                                ph.resname() + ' - Pilot', ph['uciid']
                            ]]
                if self.teamnames:
                    rno = ' '  # force name
                hlist.append([heat, rno, rname, info])
                lane += 1
                if lane > 2:
                    hno -= 1
                    lane = 1

        # sort the heatlist into front/back heat 1, 2, 3 etc
        hlist.sort(key=cmp_to_key(self.sort_heats))

        lh = None
        lcnt = 0
        rec = []
        for r in hlist:
            (h, l) = strops.heatsplit(r[0])
            if lh is not None and (h != lh or lcnt > 1):
                lcnt = 0
                ret.append(rec)
                rec = []
            heat = str(h)
            if self.difftime:  # override heat if 'final'
                heat = '-'
            if blanknames and len(r[1]) > 3:  # HACK for miss
                r[1] = ''
                r[2] = ''
                r[3] = None
            rec.extend([heat, r[1], r[2], r[3]])
            lcnt += 1
            lh = h
        if len(rec) > 0:
            ret.append(rec)
        return ret

    def get_startlist(self):
        """Return a list of bibs in the rider model."""
        ret = []
        for r in self.riders:
            ret.append(r[COL_NO])
        return ' '.join(ret)

    def delayed_announce(self):
        """Initialise the announcer's screen after a delay."""
        if self.winopen:
            # clear page
            self.meet.txt_clear()
            self.meet.txt_title(self.event.get_info(showevno=True))
            self.meet.txt_line(1)
            self.meet.txt_line(7)

            # fill in front straight
            fbib = self.fs.getrider()
            if fbib:
                r = self._getrider(fbib)
                if r is not None:
                    namestr = strops.truncpad(r[COL_NAME], 24)
                    placestr = '   '  # 3 ch
                    if r[COL_PLACE]:
                        placestr = strops.truncpad(r[COL_PLACE] + '.', 3)
                    bibstr = strops.truncpad(r[COL_NO], 3, 'r')
                    tmstr = ''
                    if r[COL_START] is not None and r[COL_FINISH] is not None:
                        tmstr = (r[COL_FINISH] - r[COL_START]).rawtime(
                            self.precision)
                    cmtstr = ''
                    if r[COL_COMMENT]:
                        cmtstr = strops.truncpad(
                            '[' + r[COL_COMMENT].strip() + ']', 38, 'r')
                    self.meet.txt_postxt(3, 0, '        Front Straight')
                    self.meet.txt_postxt(4, 0, ' '.join(
                        (placestr, bibstr, namestr)))
                    self.meet.txt_postxt(5, 26,
                                         strops.truncpad(tmstr, 12, 'r'))
                    self.meet.txt_postxt(6, 0, cmtstr)

            # fill in back straight
            bbib = self.bs.getrider()
            if bbib:
                r = self._getrider(bbib)
                if r is not None:
                    namestr = strops.truncpad(r[COL_NAME], 24)
                    placestr = '   '  # 3 ch
                    if r[COL_PLACE]:
                        placestr = strops.truncpad(r[COL_PLACE] + '.', 3)
                    bibstr = strops.truncpad(r[COL_NO], 3, 'r')
                    tmstr = ''
                    if r[COL_START] is not None and r[COL_FINISH] is not None:
                        tmstr = (r[COL_FINISH] - r[COL_START]).rawtime(
                            self.precision)
                    cmtstr = ''
                    if r[COL_COMMENT]:
                        cmtstr = strops.truncpad(
                            '[' + r[COL_COMMENT].strip() + ']', 38, 'r')
                    self.meet.txt_postxt(3, 42, '        Back Straight')
                    self.meet.txt_postxt(4, 42, ' '.join(
                        (placestr, bibstr, namestr)))
                    self.meet.txt_postxt(5, 68,
                                         strops.truncpad(tmstr, 12, 'r'))
                    self.meet.txt_postxt(6, 42, cmtstr)

            # fill in leaderboard/startlist
            count = 0
            curline = 9
            posoft = 0
            for r in self.riders:
                count += 1
                if count == 19:
                    curline = 9
                    posoft = 42
                namestr = strops.truncpad(r[COL_NAME], 22)
                placestr = '   '  # 3 ch
                if r[COL_PLACE]:
                    placestr = strops.truncpad(r[COL_PLACE] + '.', 3)
                bibstr = strops.truncpad(r[COL_NO], 3, 'r')
                tmstr = '         '  # 9 ch
                if r[COL_START] is not None and r[COL_FINISH] is not None:
                    tmstr = strops.truncpad(
                        (r[COL_FINISH] - r[COL_START]).rawtime(self.precision),
                        9, 'r')
                self.meet.txt_postxt(
                    curline, posoft, ' '.join(
                        (placestr, bibstr, namestr, tmstr)))
                curline += 1

    def do_properties(self):
        """Run race properties dialog."""
        b = uiutil.builder('ittt_properties.ui')
        dlg = b.get_object('properties')
        dlg.set_transient_for(self.meet.window)

        tt = b.get_object('race_score_type')
        if self.timetype == 'dual':
            tt.set_active(0)
        else:
            tt.set_active(1)
        di = b.get_object('race_dist_entry')
        if self.distance is not None:
            di.set_text(str(self.distance))
        else:
            di.set_text('')
        du = b.get_object('race_dist_type')
        if self.units == 'laps':
            du.set_active(1)
        else:
            du.set_active(0)
        chs = b.get_object('race_stchan_combo')
        chs.set_active(self.chan_S)
        cha = b.get_object('race_achan_combo')
        cha.set_active(self.chan_A)
        chb = b.get_object('race_bchan_combo')
        chb.set_active(self.chan_B)
        aa = b.get_object('race_autoarm_toggle')
        aa.set_active(self.autotime)
        se = b.get_object('race_series_entry')
        se.set_text(self.series)
        as_e = b.get_object('auto_starters_entry')
        as_e.set_text(self.event['starters'])
        olddistance = self.meet.get_distance(self.distance, self.units)

        response = dlg.run()
        if response == 1:  # id 1 set in glade for "Apply"
            if tt.get_active() == 1:
                self.set_timetype('single')
            else:
                self.set_timetype('dual')
            dval = di.get_text()
            if dval.isdigit():
                self.distance = int(dval)
            else:
                self.distance = None
            if du.get_active() == 0:
                self.units = 'metres'
            else:
                self.units = 'laps'

            # if distance has changed, re-initialise split data
            newdistance = self.meet.get_distance(self.distance, self.units)
            if newdistance != olddistance:
                _log.debug('Event distance changed from %r to %r', olddistance,
                           newdistance)
                self.setup_splits()

            # disable autotime if splits are not known
            self.autotime = aa.get_active()
            if not self.splitlist:
                self.autotime = False
                _log.info('No splits configured, autotime disabled')

            self.chan_S = chs.get_active()
            self.chan_A = cha.get_active()
            self.chan_B = chb.get_active()

            # update series
            ns = se.get_text()
            if ns != self.series:
                self.series = ns
                self.event['seri'] = ns

            # update auto startlist spec
            nspec = as_e.get_text()
            if nspec != self.event['starters']:
                self.event.set_value('starters', nspec)
                if not self.onestart:
                    self.riders.clear()
                    if nspec:
                        self.meet.autostart_riders(self,
                                                   nspec,
                                                   infocol=self.seedsrc)

            # xfer starters if not empty
            slist = strops.riderlist_split(
                b.get_object('race_starters_entry').get_text(), self.meet.rdb,
                self.series)

            # if no starters yet - automatically seed by order entered
            if len(self.riders) == 0:
                cnt = 1
                for s in slist:
                    self.addrider(s, cnt)
                    cnt += 1
            else:
                for s in slist:
                    self.addrider(s)
            GLib.idle_add(self.delayed_announce)
        else:
            _log.debug('Edit event properties cancelled')

        # if prefix is empty, grab input focus
        if not self.prefix_ent.get_text():
            self.prefix_ent.grab_focus()
        dlg.destroy()

    def result_gen(self):
        """Generator function to export rankings."""
        for r in self.riders:
            bib = r[COL_NO]
            rank = None
            time = None
            info = None
            cmts = r[COL_COMMENT]
            if cmts in ('caught', 'rel', 'abd', 'w/o', 'lose'):
                info = cmts
            if self.onestart:
                pls = r[COL_PLACE]
                if pls:
                    if pls.isdigit():
                        rank = int(pls)
                    else:
                        rank = pls
                if r[COL_FINISH] is not None:
                    time = (r[COL_FINISH] - r[COL_START]).truncate(
                        self.precision)

            yield (bib, rank, time, info)

    def result_report(self, recurse=False):
        """Return a list of report sections containing the race result."""
        slist = self.startlist_report()  # keep for unfinished
        finriders = set()
        self.placexfer()
        ret = []
        secid = 'ev-' + str(self.evno).translate(strops.WEBFILE_UTRANS)
        sec = report.section(secid)
        sec.nobreak = True
        sec.heading = self.event.get_info(showevno=True)
        lapstring = strops.lapstring(self.event['laps'])
        substr = ' '.join((
            lapstring,
            self.event['distance'],
            self.event['phase'],
        )).strip()
        sec.lines = []
        ftime = None
        downprec = min(self.precision, 2)
        rcount = 0
        pcount = 0
        for r in self.riders:
            rcount += 1
            rno = r[COL_NO]
            rh = self.meet.rdb.get_rider(rno, self.series)
            if rh is None:
                self.meet.rdb.add_empty(bib, self.series)
                rh = self.meet.rdb.get_rider(bib, self.series)

            rcat = None
            plink = ''
            rank = None
            rname = rh.resname()
            if self.teamnames:
                rno = ' '  # force name
            rtime = None
            # TODO: fix tandem labels
            if rh.in_cat('tandem') and rh['note']:
                ph = self.meet.rdb.get_rider(rh['note'], self.series)
                if ph is not None:
                    plink = [
                        '', '',
                        ph.resname() + ' - Pilot', ph['uciid'], '', '', ''
                    ]
            if self.showcats:
                rcat = rh.primary_cat()
            info = None
            dtime = None
            if self.onestart:
                pls = r[COL_PLACE]
                if pls:
                    if pls.isdigit():
                        rank = pls + '.'
                    else:
                        rank = pls
                    pcount += 1
                if r[COL_FINISH] is not None:
                    time = (r[COL_FINISH] - r[COL_START]).truncate(
                        self.precision)
                    if ftime is None:
                        ftime = time
                    else:
                        dtime = '+' + (time - ftime).rawtime(downprec)
                    if r[COL_START] != tod.ZERO or self.precision != 3:
                        rtime = time.rawtime(self.precision)
                    else:
                        rtime = time.rawtime(2) + '\u2007'
                elif r[COL_COMMENT]:
                    if r[COL_COMMENT] in ('catch', 'caught'):
                        rtime = str(r[COL_COMMENT])
                    elif r[COL_COMMENT] not in ('abd', 'dns', 'dsq', 'dnf'):
                        rtime = 'ntr'
            if rank:
                sec.lines.append([rank, rno, rname, rcat, rtime, dtime, plink])
                finriders.add(rno)
                # then add team members if relevant
                if self.teamnames:
                    # todo: remove madison teams from ittt
                    col = 'black'
                    for member in r[COL_MEMBERS].split():
                        trh = self.meet.rdb.fetch_bibstr(member)
                        if trh is not None:
                            trno = trh['no']
                            trinf = ''  # TODO: fix this trh['uciid']
                            trname = trh.resname()
                            if self.series == 'tmsl':  # TODO: remove
                                trno = col
                                col = 'red'
                            sec.lines.append(
                                [None, trno, trname, trinf, None, None, None])
        doheats = False
        sv = []
        if substr:
            sv.append(substr)
        if self.onestart:
            if rcount > 0 and pcount < rcount:
                sv.append('STANDINGS')
                doheats = True
            else:
                sv.append('Result')
        sec.subheading = ' - '.join(sv)

        ret.append(sec)

        if doheats and not self.difftime:
            # TODO: fix this for teams, rider no is suppressed so cannot be
            #       matched between startlist and result
            for s in slist:
                if s.sectionid == secid:  # the startlist
                    newlines = []
                    for l in s.lines:
                        if l[1] not in finriders:
                            newlines.append(l)
                    s.lines = newlines
                    if s.lines:
                        s.heading = None
                        s.subheading = 'STARTLIST'
                        ret.append(s)

        if len(self.decisions) > 0:
            ret.append(self.meet.decision_section(self.decisions))
        return ret

    def editent_cb(self, entry, col):
        """Shared event entry update callback."""
        if col == 'pref':
            self.event['pref'] = entry.get_text()
        elif col == 'info':
            self.event['info'] = entry.get_text()

    def update_expander_lbl_cb(self):
        """Update race info expander label."""
        self.info_expand.set_label(self.meet.infoline(self.event))

    def clear_rank(self, cb):
        """Run callback once in main loop idle handler."""
        cb('')
        return False

    def lap_trig(self, sp, t):
        """Register manual lap trigger."""
        # fetch cur split and sid from sp, making sure on a whole lap
        if sp.on_halflap():
            sp.lap_up()
        sid = sp.get_sid()  # might be None
        rank = self.insert_split(sid, t - self.curstart, sp.getrider())
        prev = None
        if sp.split > 1:
            prev = sp.getsplit(sp.split - 2)
        self.log_lap(sp.getrider(), sid, self.curstart, t, prev)
        # save inter time to split cache in timer, and advance split pointer
        sp.intermed(t)
        sp.lap_up()

        if self.difftime:
            if self.diffstart is None or self.difflane is sp:
                self.diffstart = t
                self.difflane = sp
            else:
                # 'other' lane has previously completed this lap
                so = self.t_other(sp)
                if so.split == sp.split and self.diffstart is not None:
                    dt = t - self.diffstart
                    if dt < 4:
                        sp.difftime(dt)
                    self.difflane = None
                    self.diffstart = None
        if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
            if rank is not None:
                rlbl = '({}) {}:'.format(rank + 1, sid)
            else:
                rlbl = '{}:'.format(sid)
            if sp is self.fs:
                self.meet.scbwin.setr1(rlbl)
                GLib.timeout_add_seconds(4, self.clear_rank,
                                         self.meet.scbwin.setr1)
                self.meet.txt_postxt(
                    5, 8,
                    strops.truncpad(rlbl, 17) + ' ' + self.fs.get_time())
            else:
                self.meet.scbwin.setr2(rlbl)
                GLib.timeout_add_seconds(4, self.clear_rank,
                                         self.meet.scbwin.setr2)
                self.meet.txt_postxt(
                    5, 50,
                    strops.truncpad(rlbl, 17) + ' ' + self.bs.get_time())

    def fin_trig(self, sp, t):
        """Register a manual finish trigger."""
        sp.finish(t)
        if self.difftime:
            if self.diffstart is None or self.difflane is sp:
                self.diffstart = t
                self.difflane = sp
            else:
                so = self.t_other(sp)
                if so.split == sp.split and self.diffstart is not None:
                    dt = t - self.diffstart
                    if dt < 4:
                        sp.difftime(dt)
                    self.difflane = None
                    self.diffstart = None
        # fetch start of last lap if possible
        prev = None
        if sp.split > 1 and not sp.on_halflap():
            # only take prev time for a whole lap at finish
            if self.splitlist and sp.split == len(self.splitlist) - 1:
                prev = sp.getsplit(sp.split - 2)
            else:
                _log.warning('Rider %r manual finish with incorrect splits',
                             sp.getrider())
        if prev is None:
            _log.warning('Last lap data not available for %r', sp.getrider())

        # update model with result
        ri = self._getiter(sp.getrider())
        if ri is not None:
            self.settimes(ri, self.curstart, t, prev, sp.splits)
        else:
            _log.warning('Rider not in model, finish time not stored')
        self.log_elapsed(sp.getrider(), self.curstart, t, sp.get_sid(), prev)

        # then report to scb, announce and result
        if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
            place = self.riders.get_value(ri, COL_PLACE)
            if sp is self.fs:
                elap = t - self.curstart
                self.meet.scbwin.setr1('(' + place + ')')
                self.meet.scbwin.sett1(self.fs.get_time())
                self.meet.gemini.set_time(self.fs.get_time(), 0)
                if self.timetype == 'single':  # Speed/TTB is hack mode
                    dist = self.meet.get_distance(self.distance, self.units)
                    if dist is not None:
                        spstr = elap.speedstr(dist).strip()
                        GLib.timeout_add_seconds(1, self.clear_200_ttb,
                                                 self.meet.scbwin, 'Avg:',
                                                 spstr.rjust(12))
                    else:
                        GLib.timeout_add_seconds(2, self.clear_200_ttb,
                                                 self.meet.scbwin)
            else:
                self.meet.scbwin.setr2('(' + place + ')')
                self.meet.scbwin.sett2(self.bs.get_time())
                self.meet.gemini.set_time(self.bs.get_time(), 1)
            self.meet.gemini.show_dual()
        # call for a delayed announce...
        GLib.idle_add(self.delayed_announce)

        # if other lane not armed, export result
        if self.t_other(sp).getstatus() != 'armfin':
            self.meet.delayed_export()

        # check for heat completion
        finished = True
        if self.fs.getrider() and self.fs.getstatus() != 'finish':
            finished = False
        if self.bs.getrider() and self.bs.getstatus() != 'finish':
            finished = False
        if finished:
            self.meet.delayimp('2.00')

    def recover_start(self):
        """Recover missed start time"""
        if self.timerstat in ('idle', 'armstart'):
            rt = self.meet.recover_time(self.chan_S)
            if rt is not None:
                # rt: (event, wallstart)
                if self.timerstat == 'idle':
                    self.toarmstart()
                if 'armstart' in (self.fs.status, self.bs.status):
                    _log.info('Recovered start time: %s', rt[0].rawtime(3))
                    self.meet.main_timer.dearm(self.chan_S)
                    self.torunning(rt[0], rt[1])
                else:
                    _log.info('No competitors loaded - recover start skipped')
            else:
                _log.info('No recent start time to recover')
        else:
            _log.info('Unable to recover start')

    def timercb(self, e):
        """Handle a timer event."""
        chan = strops.chan2id(e.chan)
        if self.timerstat == 'armstart':
            if chan == self.chan_S:
                self.torunning(e)
        elif self.timerstat == 'autotime':
            _log.warning('AUTOTIMER CALLBACK')
        elif self.timerstat == 'running':
            if chan == self.chan_A or (self.timetype == 'single'
                                       and self.chan_B):
                stat = self.fs.getstatus()
                if stat == 'armint':
                    self.lap_trig(self.fs, e)
                elif stat == 'armfin':
                    self.fin_trig(self.fs, e)
            elif chan == self.chan_B:
                stat = self.bs.getstatus()
                if stat == 'armint':
                    self.lap_trig(self.bs, e)
                elif stat == 'armfin':
                    self.fin_trig(self.bs, e)
        return False

    def timeout(self):
        """Update running time and emit to scoreboards."""
        if not self.winopen:
            return False
        now = tod.now()
        if self.fs.status in ('running', 'armint', 'armfin'):
            self.fs.runtime(now - self.lstart)
            if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                elapstr = self.fs.get_time()
                self.meet.scbwin.sett1(elapstr)
                self.meet.gemini.set_time(elapstr[0:12], lane=0)
        if self.bs.status in ('running', 'armint', 'armfin'):
            self.bs.runtime(now - self.lstart)
            if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                elapstr = self.bs.get_time()
                self.meet.scbwin.sett2(elapstr)
                self.meet.gemini.set_time(elapstr[0:12], lane=1)
        self.meet.gemini.show_dual()
        return True

    def show_200_ttb(self, scb):
        """Display time to beat."""
        if len(self.results) > 0:
            scb.setr2('Fastest:')
            scb.sett2(self.results[0].timestr(3))
        return False

    def clear_200_ttb(self, scb, r2='', t2=''):
        """Clear time to beat."""
        scb.setr2(r2)
        scb.sett2(t2)
        return False

    def torunning(self, st, wallstart=None):
        """Set timer running."""
        if self.fs.status == 'armstart':
            self.fs.start(st)
        if self.bs.status == 'armstart':
            self.bs.start(st)
        self.curstart = st
        if wallstart is None:
            wallstart = tod.now()
        self.lstart = wallstart
        self.diffstart = None
        self.difflane = None
        if self.autotime:
            self.timerstat = 'autotime'
        else:
            self.timerstat = 'running'
        self.onestart = True
        if self.timetype == 'single':
            pass

    def clearplaces(self):
        """Clear rider places."""
        for r in self.riders:
            r[COL_PLACE] = ''

    def inevent(self, bib):
        """Return true if rider appears in model."""
        return self._getrider(bib) is not None

    def _getrider(self, bib):
        """Return temporary reference to model row."""
        bib = bib.upper()
        ret = None
        for r in self.riders:
            if r[COL_NO] == bib:
                ret = r
                break
        return ret

    def _getiter(self, bib):
        """Return temporary iterator to model row."""
        bib = bib.upper()
        i = self.riders.get_iter_first()
        while i is not None:
            if self.riders.get_value(i, COL_NO) == bib:
                break
            i = self.riders.iter_next(i)
        return i

    def delrider(self, bib):
        # Issue warning if removed rider in result
        bib = bib.upper()
        if self.results.rank(bib) is not None:
            _log.warning('Removed rider %r was in event %r result', bib,
                         self.evno)
            self.results.remove(bib)
            for split in self.splitap.values():
                split['data'].remove(bib)
            if bib in self.traces:
                del self.traces[bib]
        elif 'fsbib' in self._winState and self._winState['fsbib'].upper(
        ) == bib:
            _log.warning('Removed rider %r in event %r front timer', bib,
                         self.evno)
        elif 'bsbib' in self._winState and self._winState['bsbib'].upper(
        ) == bib:
            _log.warning('Removed rider %r in event %r back timer', bib,
                         self.evno)

        i = self._getiter(bib)
        if i is not None:
            self.riders.remove(i)

    def changerider(self, oldNo, newNo):
        """Update rider no in event"""
        oldNo = oldNo.upper()
        newNo = newNo.upper()
        if self.inevent(oldNo):
            if oldNo != newNo and not self.inevent(newNo):
                name = ''
                dbr = self.meet.rdb.get_rider(newNo, self.series)
                if dbr is not None:
                    name = dbr.listname()
                for r in self.riders:
                    if r[COL_NO] == oldNo:
                        _log.debug('Updating number %s -> %s in event %s',
                                   oldNo, newNo, self.evno)
                        r[COL_NO] = newNo
                        r[COL_NAME] = name
                        break
                for split in self.splitmap.values():
                    split['data'].changeno(oldNo, newNo)
                self.results.changeno(oldNo, newNo)
                if oldNo in self.traces:
                    self.traces[newNo] = self.traces[oldNo]
                    del self.traces[oldNo]
                return True
        return False

    def addrider(self, bib='', info=None):
        """Add specified rider to race model."""
        bib = bib.upper()
        istr = ''
        if info is not None:
            istr = str(info)
        ri = self._getrider(bib)
        if ri is None:  # adding a new record
            nr = [bib, '', '', '', '', istr, '', None, None, None, None]
            dbr = self.meet.rdb.get_rider(bib, self.series)
            if dbr is not None:
                nr[COL_NAME] = dbr.listname()
            self.riders.append(nr)
        else:
            # rider exists in model, just update the seed value
            ri[COL_SEED] = istr

    def _editseed_cb(self, cell, path, new_text, col):
        """Edit the rider seeding."""
        old_text = self.riders[path][col]
        if old_text != new_text:
            self.riders[path][col] = new_text

    def _editmembers_cb(self, cell, path, new_text, col):
        """Edit the team members list."""
        old_text = self.riders[path][col]
        if old_text != new_text:
            nr = []
            for rno in new_text.split():
                nno = strops.bibstr(rno)
                if nno not in nr:
                    nr.append(nno)
            self.riders[path][col] = ' '.join(nr)
            dbr = self.meet.rdb.get_rider(self.riders[path][COL_NO],
                                          self.series)
            if dbr is not None:
                newmbrs = []
                oldmbrs = dbr['members'].split()
                for rno in oldmbrs:
                    nno = strops.bibstr(rno)
                    newmbrs.append(nno)
                for rno in nr:
                    if rno not in newmbrs:
                        newmbrs.append(rno)
                dbr['members'] = ' '.join(newmbrs)

    def _editname_cb(self, cell, path, new_text, col):
        """Edit the rider name if possible."""
        old_text = self.riders[path][col]
        if old_text != new_text:
            self.riders[path][col] = new_text
            rNo = self.riders[path][COL_NO]
            dbr = self.meet.rdb.get_rider(rNo, self.series)
            if dbr is None:
                # Assume one is required
                self.meet.rdb.add_empty(rNo, self.series)
                dbr = self.meet.rdb.get_rider(rNo, self.series)
            _log.debug('Updating %s %s detail', dbr.get_label(), dbr.get_id())
            dbr.rename(new_text)

    def placexfer(self):
        """Transfer places into model."""
        self.finished = False
        self.clearplaces()
        count = 0
        place = 1
        for t in self.results:
            bib = t[0].refid
            if t[0] > tod.FAKETIMES['max']:
                if t[0] in (tod.FAKETIMES['caught'], tod.FAKETIMES['lose'],
                            tod.FAKETIMES['rel'], tod.FAKETIMES['caught']):
                    place = self.results.rank(bib) + 1
                    self.onestart = True
                elif t[0] == tod.FAKETIMES['abd']:
                    place = 'abd'
                elif t[0] == tod.FAKETIMES['dsq']:
                    place = 'dsq'
                elif t[0] == tod.FAKETIMES['dns']:
                    place = 'dns'
                elif t[0] == tod.FAKETIMES['dnf']:
                    place = 'dnf'
            else:
                place = self.results.rank(bib) + 1
                self.onestart = True
            i = self._getiter(bib)
            if i is not None:
                if place == 'comment':  # superfluous but ok
                    place = self.riders.get_value(i, COL_COMMENT)
                self.riders.set_value(i, COL_PLACE, str(place))
                self.riders.swap(self.riders.get_iter(count), i)
                count += 1
            else:
                _log.warning('Rider %r not found in model, check places', bib)
        tcount = len(self.riders)
        self._standingstr = ''
        if tcount > 0 and count > 0:
            if tcount == count:
                self._standingstr = 'Result'
                self.finished = True
            else:
                self._standingstr = 'Virtual Standing'

    def settimes(self,
                 iter,
                 st=None,
                 ft=None,
                 lt=None,
                 splits=None,
                 doplaces=True,
                 comment=None):
        """Transfer race times into rider model."""
        bib = self.riders.get_value(iter, COL_NO)
        # clear result for this bib
        self.results.remove(bib)
        # assign tods
        self.riders.set_value(iter, COL_START, st)
        self.riders.set_value(iter, COL_FINISH, ft)
        self.riders.set_value(iter, COL_LASTLAP, lt)
        # save result
        if st is None:
            st = tod.ZERO
        if ft is not None:
            lastlap = None
            if lt is not None:
                lastlap = (ft - lt).truncate(self.precision)
            self.results.insert((ft - st).truncate(self.precision), lastlap,
                                bib)
        else:  # DNF/Catch/etc
            self.results.insert(comment, None, bib)
        if splits is not None:
            # save reference to rider model
            self.riders.set_value(iter, COL_SPLITS, splits)
            for sid, split in splits.items():
                # and transfer into inter-ranks
                if sid in self.splitmap:
                    self.splitmap[sid]['data'].remove(bib)
                    if split is not None:
                        splitval = split - st
                        self.splitmap[sid]['data'].insert(splitval, None, bib)
                else:
                    _log.info('Unknown split %r for rider %r', sid, bib)

        # copy annotation into model if provided, or clear
        if comment:
            self.riders.set_value(iter, COL_COMMENT, comment)
        else:
            self.riders.set_value(iter, COL_COMMENT, '')
        # if reqd, do places
        if doplaces:
            self.placexfer()

    def insert_split(self, sid, st, bib):
        """Insert a rider split into correct lap."""
        ret = None
        if sid in self.splitmap:
            self.splitmap[sid]['data'].insert(st, None, bib)
            ret = self.splitmap[sid]['data'].rank(bib)
        else:
            _log.debug('No ranking for rider %r at unknown split %r', bib, sid)
        return ret

    def armstart(self):
        """Arm timer for start trigger."""
        if self.timerstat == 'armstart':
            self.toload()
        elif self.timerstat in ('load', 'idle'):
            self.toarmstart()

    def disable_autotime(self):
        """Cancel a running autotime for manual intervention."""
        if self.timerstat == 'autotime':
            _log.error('DISABLE AUTOTIMER')
            self.timerstat = 'running'

    def armlap(self, sp, cid):
        """Arm timer for a manual lap split."""
        if self.timerstat == 'autotime':
            _log.info('Autotime disabled by manual intervention')
            self.disable_autotime()
        if self.timerstat == 'running':
            if sp.getstatus() in ('caught', 'running'):
                if sp.on_halflap():
                    sp.lap_up()
                if sp.split < len(self.splitlist) - 1:
                    sp.toarmint()
                else:
                    _log.info('Rider %r approaching last lap, armfinish',
                              sp.getrider())
                    sp.toarmfin()
                self.meet.main_timer.arm(cid)
            elif sp.getstatus() == 'armint':
                sp.torunning()
                self.meet.main_timer.dearm(cid)

    def lanestr(self, sp):
        """Return f for front and b for back straight."""
        ret = 'f'
        if sp is self.bs:
            ret = 'b'
        return ret

    def abortrider(self, sp):
        """Abort the selected lane."""
        if sp.getstatus() not in ('idle', 'caught', 'finish'):
            bib = sp.getrider()
            ri = self._getiter(bib)
            if ri is not None:
                self.settimes(ri,
                              st=self.curstart,
                              splits=sp.splits,
                              comment='abort')
            sp.tofinish()
            self.meet.timer_log_msg(bib, '- Abort -')
            GLib.idle_add(self.delayed_announce)

    def catchrider(self, sp):
        """Selected lane has caught other rider."""
        if not self.difftime:
            # heat is not terminated by catch of rider, just log details
            _log.info('Rider %r catch ignored', sp.getrider())
        elif self.timetype != 'single':
            op = self.t_other(sp)
            if op.getstatus() not in ('idle', 'finish'):
                bib = op.getrider()
                ri = self._getiter(bib)

                if ri is not None:
                    self.settimes(ri,
                                  st=self.curstart,
                                  splits=op.splits,
                                  comment='caught')
                op.tofinish('caught')
                self.meet.timer_log_msg(bib, '- Caught -')
                if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                    if op is self.fs:
                        self.meet.scbwin.sett1(' [caught]     ')
                        self.meet.gemini.set_time('    -:--.-  ', 0)
                    else:
                        self.meet.scbwin.sett2(' [caught]     ')
                        self.meet.gemini.set_time('    -:--.-  ', 1)
            if sp.getstatus() not in ('idle', 'finish'):
                bib = sp.getrider()
                ri = self._getiter(bib)
                if ri is not None:
                    self.settimes(ri,
                                  st=self.curstart,
                                  splits=sp.splits,
                                  comment='catch')
                self.meet.timer_log_msg(bib, '- Catch -')
                # but continue by default - manual abort to override.
            GLib.idle_add(self.delayed_announce)
        else:
            _log.warning('Unable to catch with single rider')

    def falsestart(self):
        """Register false start."""
        if self.timerstat == 'autotime':
            self.disable_autotime()
        if self.timerstat == 'running':
            if self.fs.getstatus() not in ('idle', 'caught', 'finish'):
                self.fs.toload()
                self.meet.timer_log_msg(self.fs.getrider(), '- False start -')
                if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                    self.meet.scbwin.setr1('False')
                    self.meet.scbwin.sett1('Start')
            if self.bs.getstatus() not in ('idle', 'caught', 'finish'):
                self.bs.toload()
                self.meet.timer_log_msg(self.bs.getrider(), '- False start -')
                if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                    self.meet.scbwin.setr2('False')
                    self.meet.scbwin.sett2('Start')
            self.toidle(idletimers=False)
        elif self.timerstat == 'armstart':
            if self.timerwin and type(self.meet.scbwin) is scbwin.scbtt:
                self.meet.gemini.clear()
                self.meet.scbwin.sett1('            ')
                self.meet.scbwin.sett2('            ')
            self.toload()

    def armfinish(self, sp, cid):
        """Arm timer for finish trigger."""
        if self.timerstat == 'autotime':
            _log.info('Autotime disabled by manual intervention')
            self.disable_autotime()
        if self.timerstat == 'running':
            if sp.getstatus() in ('running', 'caught', 'finish'):
                if sp.getstatus() == 'finish':
                    self.meet.timer_log_msg(sp.getrider(), '- False finish -')
                    self.meet.scbwin.setr1('')
                    self.meet.scbwin.setr2('')
                sp.toarmfin()
                self.meet.main_timer.arm(cid)
            elif sp.getstatus() == 'armfin':
                sp.torunning()
                self.meet.main_timer.dearm(cid)

    def toload(self):
        """Set timer status to load."""
        if self.fs.status == 'armstart':
            self.fs.toload()
        if self.bs.status == 'armstart':
            self.bs.toload()
        self.toidle(idletimers=False)

    def _getname(self, bib, width=32):
        """Return a name and club for the rider if known"""
        name = ''
        club = ''
        dbr = self.meet.rdb.get_rider(bib, self.series)
        if dbr is not None:
            name = dbr.fitname(width)
            club = dbr['organisation']
        return name, club

    def fmtmembers(self, tp):
        """Prepare the team member name lines for display."""
        ret = None
        if self.teamnames:
            name_w = self.meet.scb.linelen // 2 - 5
            fmt = (' ', (3, 'r'), ' ', (name_w, 'l'))
            bib = tp.getrider().strip()
            if bib != '':
                r = self._getrider(bib)
                if r is not None and r[COL_NO]:
                    tn = []
                    mc = 0
                    for trno in r[COL_MEMBERS].split():
                        trh = self.meet.rdb.fetch_bibstr(trno)
                        if trh is not None:
                            tn.append(
                                scbwin.fmt_row(
                                    fmt,
                                    (trh['no'], trh.fitname(width=name_w))))
                            mc += 1
                    if mc == 1:
                        ret = (tn[0], '')
                    elif mc == 2:
                        ret = (tn[0] + tn[1], '')
                    elif mc == 3:
                        ret = (tn[0] + tn[1], tn[2])
                    else:
                        ret = (tn[0] + tn[1], tn[2] + tn[3])
        return ret

    def fmtridername(self, tp):
        """Prepare rider name for display on scoreboard."""
        bib = tp.getrider().strip()
        if bib != '':
            ret = ''
            name = ''
            club = ''
            r = self._getrider(bib)
            if r is not None and r[COL_NO]:
                if self.teamnames:
                    name_w = self.meet.scb.linelen - 5
                else:
                    name_w = self.meet.scb.linelen - 9
                name, club = self._getname(r[COL_NO], width=name_w)
                if len(club) != 3:
                    club = ''
                if self.teamnames:
                    fmt = ((name_w, 'l'), (5, 'r'))
                    row = (name, club)
                    ret = scbwin.fmt_row(fmt, row)
                else:
                    fmt = ((3, 'r'), ' ', (name_w, 'l'), (5, 'r'))
                    row = (r[COL_NO], name, club)
                    ret = scbwin.fmt_row(fmt, row)
            return ret
        else:
            return ''

    def showtimerwin(self):
        """Show timer window on scoreboard."""
        self.meet.scbwin = None
        self.meet.scbwin = scbwin.scbtt(self.meet.scb,
                                        self.meet.racenamecat(self.event),
                                        self.fmtridername(self.fs),
                                        self.fmtridername(self.bs),
                                        team1=self.fmtmembers(self.fs),
                                        team2=self.fmtmembers(self.bs))
        if self.timetype == 'single':
            self.meet.scbwin.set_single()
        self.meet.gemini.reset_fields()
        self.meet.gemini.set_bib(self.fs.getrider(), 0)
        self.meet.gemini.set_bib(self.bs.getrider(), 1)
        self.timerwin = True
        self.meet.scbwin.reset()

    def toarmstart(self):
        """Set timer to arm start."""
        doarm = False
        if self.fs.status == 'load':
            self.fs.toarmstart()
            doarm = True
        if self.bs.status == 'load' and self.timetype != 'single':
            self.bs.toarmstart()
            doarm = True
        if doarm:
            self.meet.timer_log_event(self.event)
            self.timerstat = 'armstart'
            self.curstart = None
            self.lstart = None
            self.meet.main_timer.arm(self.chan_S)
            self.showtimerwin()
            self.meet.delayimp('0.01')
            if self.fs.status == 'armstart':
                bib = self.fs.getrider()
                if bib not in self.traces:
                    self.traces[bib] = []
                self.fslog = uiutil.traceHandler(self.traces[bib])
                logging.getLogger().addHandler(self.fslog)
                self.meet.scbwin.sett1('       0.0     ')
                nstr = self.fs.biblbl.get_text()
                self.meet.timer_log_msg(bib, nstr)
            if self.bs.status == 'armstart':
                bib = self.bs.getrider()
                if bib not in self.traces:
                    self.traces[bib] = []
                self.bslog = uiutil.traceHandler(self.traces[bib])
                logging.getLogger().addHandler(self.bslog)
                self.meet.scbwin.sett2('       0.0     ')
                nstr = self.bs.biblbl.get_text()
                self.meet.timer_log_msg(bib, nstr)
            if self.timetype == 'single':
                self.bs.toidle()
                self.bs.disable()
            GLib.idle_add(self.delayed_announce)

    def toidle(self, idletimers=True):
        """Set timer to idle state."""
        if self.timerstat == 'autotime':
            self.disable_autotime()
        if self.fslog is not None:
            logging.getLogger().removeHandler(self.fslog)
            self.fslog = None
        if self.bslog is not None:
            logging.getLogger().removeHandler(self.bslog)
            self.bslog = None
        if idletimers:
            self.fs.toidle()
            self.bs.toidle()
        self.timerstat = 'idle'
        self.meet.delayimp('2.00')
        self.curstart = None
        self.lstart = None
        self.diffstart = None
        for i in range(0, 8):
            self.meet.main_timer.dearm(i)
        if not self.onestart:
            pass
        self.fs.grab_focus()

    def t_other(self, tp=None):
        """Return reference to 'other' timer."""
        if tp is self.fs:
            return self.bs
        else:
            return self.fs

    def lanelookup(self, bib=None):
        """Prepare name string for timer lane."""
        r = self._getrider(bib)
        if r is None:
            if self.meet.get_clubmode():
                _log.warning('Adding non-starter %r', bib)
                self.addrider(bib)
                r = self._getrider(bib)
            else:
                _log.warning('Rider %r not in event', bib)
                return None
        rtxt = '[New Rider]'
        if r is not None:
            rtxt = r[COL_NAME]
        return rtxt

    def bibent_cb(self, entry, tp):
        """Bib entry callback."""
        bib = entry.get_text().strip().upper()
        if bib != '' and bib.isalnum():
            nstr = self.lanelookup(bib)
            if nstr is not None:
                tp.biblbl.set_text(nstr)
                if tp.status == 'idle':
                    tp.toload()
                if self.timerstat == 'autotime':
                    _log.info('HANDLE JOIN OF TIMER AFTER AUTOTIME START')
                    tp.start(self.curstart)
                if self.timerstat == 'running':
                    tp.start(self.curstart)
                if self.timetype != 'single':
                    self.t_other(tp).grab_focus()
            else:
                _log.warning('Ignoring non-starter: %r', bib)
                tp.toidle()
        else:
            tp.toidle()

    def treeview_button_press(self, treeview, event):
        """Set callback for mouse press on model view."""
        if event.button == 3:
            pathinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
            if pathinfo is not None:
                path, col, cellx, celly = pathinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, False)
                self.context_menu.popup_at_pointer(None)
                return True
        return False

    def tod_context_clear_activate_cb(self, menuitem, data=None):
        """Clear times for selected rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1])
            self.log_clear(self.riders.get_value(sel[1], COL_NO))
            GLib.idle_add(self.delayed_announce)

    def tod_context_abd_activate_cb(self, menuitem, data=None):
        """Abandon rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='abd')
            GLib.idle_add(self.delayed_announce)

    def tod_context_rel_activate_cb(self, menuitem, data=None):
        """Relegate rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='rel')
            GLib.idle_add(self.delayed_announce)

    def tod_context_ntr_activate_cb(self, menuitem, data=None):
        """No time recorded for rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='ntr')
            GLib.idle_add(self.delayed_announce)

    def tod_context_dnf_activate_cb(self, menuitem, data=None):
        """DNF rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='dnf')
            GLib.idle_add(self.delayed_announce)

    def tod_context_dsq_activate_cb(self, menuitem, data=None):
        """Disqualify rider."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='dsq')
            GLib.idle_add(self.delayed_announce)

    def tod_context_dns_activate_cb(self, menuitem, data=None):
        """Rider did not start."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            self.settimes(sel[1], comment='dns')
            GLib.idle_add(self.delayed_announce)

    def tod_context_print_activate_cb(self, menuitem, data=None):
        """Print Rider trace"""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            bib = self.riders.get_value(sel[1], COL_NO)
            if bib in self.traces:
                secid = 'trace-' + str(bib).translate(strops.WEBFILE_UTRANS)
                sec = report.preformat_text(secid)
                sec.nobreak = True
                sec.lines = self.traces[bib]
                self.meet.print_report([sec], 'Timing Trace')

    def now_button_clicked_cb(self, button, entry=None):
        """Set specified entry to the current time."""
        if entry is not None:
            entry.set_text(tod.now().timestr())

    def tod_context_edit_activate_cb(self, menuitem, data=None):
        """Run edit time dialog."""
        sel = self.view.get_selection().get_selected()
        if sel is None:
            return False

        i = sel[1]
        lr = Gtk.TreeModelRow(self.riders, i)
        namestr = lr[COL_NO]
        dbr = self.meet.rdb.get_rider(lr[COL_NO], self.series)
        if dbr is not None:
            namestr = dbr.resname_bib()
        placestr = ''
        placeopts = {
            '': ' Not yet classified',
            'ntr': 'No time recorded',
            'abd': 'Abandon',
            'dns': 'Did not start',
            'otl': 'Outside time limit',
            'dnf': 'Did not finish',
            'dsq': 'Disqualified',
        }
        if lr[COL_PLACE] and lr[COL_PLACE] not in placeopts:
            placestr = 'Ranked ' + strops.rank2ord(lr[COL_PLACE])
            if lr[COL_COMMENT]:
                placestr += ' (' + lr[COL_COMMENT] + ')'
        elif lr[COL_PLACE] in placeopts:
            placestr = placeopts[lr[COL_PLACE]]
        else:
            placestr = placeopts['']

        sections = {
            'result': {
                'object': None,
                'title': 'result',
                'schema': {
                    'title': {
                        'prompt': namestr,
                        'control': 'section',
                    },
                    'class': {
                        'prompt': 'Classification:',
                        'hint': 'Rider classification for event',
                        'control': 'label',
                        'value': placestr,
                    },
                    'start': {
                        'prompt': 'Start:',
                        'hint': 'Recorded start time',
                        'type': 'tod',
                        'places': 4,
                        'value': lr[COL_START],
                        'nowbut': True,
                        'control': 'short',
                        'subtext': 'Set start time to now',
                        'index': COL_START,
                    },
                    'finish': {
                        'prompt': 'Finish:',
                        'hint': 'Recorded finish time',
                        'type': 'tod',
                        'places': 4,
                        'value': lr[COL_FINISH],
                        'nowbut': True,
                        'control': 'short',
                        'subtext': 'Set finish time to now',
                        'index': COL_FINISH,
                    },
                },
            },
        }
        res = uiutil.options_dlg(window=self.meet.window,
                                 title='Edit times',
                                 sections=sections)
        changed = False
        dotimes = False
        for option in res['result']:
            if res['result'][option][0]:
                changed = True
                if 'index' in sections['result']['schema'][option]:
                    index = sections['result']['schema'][option]['index']
                    lr[index] = res['result'][option][2]
                    _log.debug('Updated %s to: %r', option,
                               res['result'][option][2])
                    if option in ('start', 'finish'):
                        dotimes = True
                else:
                    _log.debug('Unknown option %r changed', option)
        if dotimes:
            bib = lr[COL_NO]
            stod = lr[COL_START]
            ftod = lr[COL_FINISH]
            if stod is not None and ftod is not None:
                self.settimes(i, stod, ftod)
                self.log_elapsed(bib, stod, ftod, manual=True)
            else:
                self.settimes(i)
                self.log_clear(bib)
            _log.info('Race times manually adjusted for rider %r', bib)
            GLib.idle_add(self.delayed_announce)

    def tod_context_del_activate_cb(self, menuitem, data=None):
        """Delete selected row from race model."""
        sel = self.view.get_selection().get_selected()
        if sel is not None:
            i = sel[1]  # grab off row iter
            if self.riders.remove(i):
                pass  # re-select?
            GLib.idle_add(self.delayed_announce)

    def log_clear(self, bib):
        """Print clear time log."""
        self.meet.timer_log_msg(bib, '- Time Cleared -')

    def log_lap(self, bib, sid, start, split, prev=None):
        """Print a split log."""
        if prev is None:
            prev = start
        self.meet.timer_log_straight(bib, sid, split - prev, 3)
        if prev != start:
            self.meet.timer_log_straight(bib, 'time', split - start, 3)

    def log_elapsed(self,
                    bib,
                    start,
                    finish,
                    sid=None,
                    prev=None,
                    manual=False):
        """Print elapsed log info."""
        if manual:
            self.meet.timer_log_msg(bib, '- Manual Adjust -')
        if prev is not None and prev != start:
            self.meet.timer_log_straight(bib, sid, finish - prev, 3)
        self.meet.timer_log_straight(bib, 'ST', start)
        self.meet.timer_log_straight(bib, 'FIN', finish)
        self.meet.timer_log_straight(bib, 'TIME', finish - start, 3)

    def set_timetype(self, data=None):
        """Update timer panes to match timetype or data if provided."""
        if data is not None:
            self.timetype = strops.confopt_pair(data, 'single', 'dual')
        if self.winopen:
            if self.timetype == 'single':
                self.bs.frame.hide()
                self.bs.hide_splits()
                self.fs.frame.set_label('Timer')
                self.fs.show_splits()
            else:
                self.bs.frame.show()
                self.bs.show_splits()
                self.fs.frame.set_label('Front Straight')
                self.fs.show_splits()

    def show(self):
        """Show race window."""
        self.frame.show()

    def hide(self):
        """Hide race window."""
        self.frame.hide()

    def __init__(self, meet, event, ui=True):
        """Constructor."""
        self.meet = meet
        self.event = event
        self.evno = event['evid']
        self.evtype = event['type']
        self.series = event['seri']
        self.configfile = meet.event_configfile(self.evno)

        self.readonly = not ui
        rstr = ''
        if self.readonly:
            rstr = 'readonly '
        _log.debug('Init %sevent %s', rstr, self.evno)

        # properties
        self.timetype = 'dual'
        self.distance = None
        self.units = 'laps'
        self.autotime = False
        self.decisions = []
        self.difftime = False
        self.precision = 3
        self.teampursuit = False
        self.teamnames = False  # team names only shown
        self.chan_A = 2  # default is ITT/Pursuit
        self.chan_B = 3
        self.chan_S = 0
        self.fsvec = None
        self.bsvec = None
        self.fslog = None
        self.bslog = None
        self._winState = {}

        # race run time attributes
        self._standingstr = ''
        self.finished = False
        self.inomnium = False
        self.seedsrc = 1  # default seeding is by rank in last round
        self.onestart = False
        self.winopen = ui
        self.timerwin = False
        self.showcats = False
        self.timerstat = 'idle'
        self.curstart = None
        self.lstart = None
        self.diffstart = None  # for diff time in pursuit race
        self.difflane = None  # for diff time in pursuit race
        self.splitlist = []  # ordered list of split ids
        self.splitmap = {}  # map of split ids and rank data
        self.results = tod.todlist('FIN')
        self.context_menu = None
        self.traces = {}
        self._winState = {}  # cache ui settings for headless load/save

        self.riders = Gtk.ListStore(
            str,  # 0 bib
            str,  # 1 name
            str,  # 2 reserved
            str,  # 3 team members
            str,  # 4 Comment
            str,  # 5 seeding
            str,  # 6 place
            object,  # 7 Start
            object,  # 8 Finish
            object,  # 9 Last Lap
            object)  # 10 Splits

        if ui:
            b = uiutil.builder('ittt.ui')
            self.frame = b.get_object('race_vbox')

            # meta info pane
            self.info_expand = b.get_object('info_expand')
            b.get_object('race_info_evno').set_text(self.evno)
            self.showev = b.get_object('race_info_evno_show')
            self.prefix_ent = b.get_object('race_info_prefix')
            self.prefix_ent.connect('changed', self.editent_cb, 'pref')
            self.prefix_ent.set_text(self.event['pref'])
            self.info_ent = b.get_object('race_info_title')
            self.info_ent.connect('changed', self.editent_cb, 'info')
            self.info_ent.set_text(self.event['info'])

            # Timer Panes
            mf = b.get_object('race_timer_pane')
            self.fs = uiutil.timerpane('Front Straight', doser=False)
            self.fs.bibent.connect('activate', self.bibent_cb, self.fs)
            self.bs = uiutil.timerpane('Back Straight', doser=False)
            self.bs.urow = 6  # scb row for timer messages
            self.bs.bibent.connect('activate', self.bibent_cb, self.bs)
            mf.pack_start(self.fs.frame, True, True, 0)
            mf.pack_start(self.bs.frame, True, True, 0)
            mf.set_focus_chain([self.fs.frame, self.bs.frame, self.fs.frame])

            # riders pane
            t = Gtk.TreeView(self.riders)
            self.view = t
            t.set_reorderable(True)
            t.set_enable_search(False)
            t.set_rules_hint(True)
            t.connect('button_press_event', self.treeview_button_press)

            uiutil.mkviewcoltxt(t, 'No.', COL_NO, calign=1.0)
            uiutil.mkviewcoltxt(t,
                                'Name',
                                COL_NAME,
                                self._editname_cb,
                                expand=True)
            uiutil.mkviewcoltxt(t, 'Members', COL_MEMBERS,
                                self._editmembers_cb)
            uiutil.mkviewcoltxt(t, 'Seed', COL_SEED, self._editseed_cb)
            uiutil.mkviewcoltod(t, 'Time/Last Lap', cb=self.todstr)
            uiutil.mkviewcoltxt(t, 'Rank', COL_PLACE, halign=0.5, calign=0.5)
            self.view.get_column(_VIEWCOL_MEMBERS).set_visible(False)

            t.show()
            b.get_object('race_result_win').add(t)
            self.context_menu = b.get_object('rider_context')
            b.connect_signals(self)
