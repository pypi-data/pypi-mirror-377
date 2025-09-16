# SPDX-License-Identifier: MIT
"""Timing and data handling application wrapper for road events."""
__version__ = '1.13.13'

import sys
import gi
import logging
import metarace
from metarace import htlib
import csv
import os
import threading
from contextlib import suppress

gi.require_version("GLib", "2.0")
from gi.repository import GLib

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

from metarace import jsonconfig
from metarace import tod
from metarace import riderdb
from metarace.telegraph import telegraph, _CONFIG_SCHEMA as _TG_SCHEMA
from metarace.export import mirror, _CONFIG_SCHEMA as _EXPORT_SCHEMA
from metarace.decoder import decoder
from metarace.decoder.rru import rru, _CONFIG_SCHEMA as _RRU_SCHEMA
from metarace.decoder.rrs import rrs, _CONFIG_SCHEMA as _RRS_SCHEMA
from metarace.decoder.thbc import thbc, _CONFIG_SCHEMA as _THBC_SCHEMA
from metarace.timy import timy, _TIMER_LOG_LEVEL, _CONFIG_SCHEMA as _TIMY_SCHEMA
from metarace import strops
from metarace import report

from . import uiutil
from roadmeet.rms import rms, _CONFIG_SCHEMA as _RMS_SCHEMA
from roadmeet.irtt import irtt, _CONFIG_SCHEMA as _IRTT_SCHEMA
from roadmeet.trtt import trtt, _CONFIG_SCHEMA as _TRTT_SCHEMA
from roadmeet.drelay import _CONFIG_SCHEMA as _DRELAY_SCHEMA

PRGNAME = 'org.6_v.roadmeet'
APPNAME = 'Roadmeet'
LOGFILE = 'event.log'
LOGFILE_LEVEL = logging.DEBUG
CONFIGFILE = 'config.json'
ROADMEET_ID = 'roadmeet-3.2'  # configuration versioning
EXPORTPATH = 'export'
_log = logging.getLogger('roadmeet')
_log.setLevel(logging.DEBUG)
ROADRACE_TYPES = {
    'road': 'Road Race',
    'circuit': 'Circuit',
    'criterium': 'Criterium',
    'handicap': 'Handicap',
    'cross': 'Cyclocross',
    'irtt': 'Individual Time Trial',
    'trtt': 'Team Time Trial',
}
PRINT_TYPES = {
    'save': 'Save to PDF',
    'pdfpreview': 'Preview and Save to PDF',
    'preview': 'Preview',
    'dialog': 'Print Dialog',
    'direct': 'Print Direct'
}
_HANDLERS = {
    'null': decoder,
    'thbc': thbc,
    'rrs': rrs,
    'rru': rru,
}
_COLOURMAP = {
    'dark': (
        'darkgreen',
        'chocolate',
        'darkblue',
        'darkred',
        'teal',
        'darkmagenta',
        'dimgrey',
    ),
    'light': (
        'lightgreen',
        'orange',
        'lightskyblue',
        'lightcoral',
        'turquoise',
        'violet',
        'lightgrey',
    ),
}
_CONFIG_SCHEMA = {
    'mtype': {
        'prompt': 'Meet Information',
        'control': 'section',
    },
    'etype': {
        'prompt': 'Type:',
        'control': 'choice',
        'attr': 'etype',
        'defer': True,
        'options': ROADRACE_TYPES,
        'default': 'road',
    },
    'title': {
        'prompt': 'Title:',
        'hint': 'Meet title',
        'attr': 'title',
        'default': '',
    },
    'subtitle': {
        'prompt': 'Subtitle:',
        'hint': 'Meet subtitle',
        'attr': 'subtitle',
        'default': '',
    },
    'host': {
        'prompt': 'Host:',
        'hint': 'Text for the meet host / sponsor line',
        'attr': 'host',
        'default': '',
    },
    'document': {
        'prompt': 'Location:',
        'hint': 'Text for the meet location / document line',
        'attr': 'document',
        'default': '',
    },
    'date': {
        'prompt': 'Date:',
        'hint': 'Date of the meet as human-readable text',
        'attr': 'date',
        'default': '',
    },
    'pcp': {
        'prompt': 'PCP:',
        'hint': 'Name of the president of the commissaires panel',
        'attr': 'pcp',
        'default': '',
    },
    'organiser': {
        'prompt': 'Organiser:',
        'hint': 'Name of the meet organiser',
        'attr': 'organiser',
        'default': '',
    },
    'distance': {
        'prompt': 'Distance:',
        'hint': 'Advertised distance of the meet (if applicable)',
        'type': 'float',
        'control': 'short',
        'subtext': 'km',
        'attr': 'distance'
    },
    'diststr': {
        'prompt': 'Dist String:',
        'hint': 'Override distance string for crit/cat races',
        'attr': 'diststr',
        'default': '',
    },
    'minavg': {
        'prompt': 'Min Avg:',
        'hint': 'Minimum reported average speed',
        'type': 'float',
        'control': 'short',
        'subtext': 'km/h',
        'attr': 'minavg',
        'places': 1,
        'default': 20.0,
    },
    'maxavg': {
        'prompt': 'Max Avg:',
        'hint': 'Maximum reported average speed',
        'type': 'float',
        'control': 'short',
        'subtext': 'km/h',
        'attr': 'maxavg',
        'places': 1,
        'default': 60.0,
    },
    'provisionalstart': {
        'prompt': 'Startlist:',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Provisional?',
        'hint': 'Mark startlist reports as provisional',
        'attr': 'provisionalstart',
        'default': True,
    },
    'doprint': {
        'prompt': 'Reports:',
        'control': 'choice',
        'attr': 'doprint',
        'defer': True,
        'options': PRINT_TYPES,
        'default': 'preview',
        'hint': 'Ad-hoc report handling'
    },
    'sectele': {
        'control': 'section',
        'prompt': 'Telegraph',
    },
    'anntopic': {
        'prompt': 'Announce:',
        'hint': 'Base topic for announcer messages',
        'attr': 'anntopic',
    },
    'announceresult': {
        'prompt': 'Announce Result:',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Publish result to telegraph?',
        'hint': 'Announce result to telegraph on export',
        'attr': 'announceresult',
        'default': False,
    },
    'timertopic': {
        'prompt': 'Timer:',
        'hint': 'Full topic for timer messages',
        'attr': 'timertopic',
    },
    'remoteenable': {
        'prompt': '',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Receive remote timer messages?',
        'hint': 'Receive remote timer messages from timer topic',
        'attr': 'remoteenable',
        'default': False,
    },
    'sechw': {
        'control': 'section',
        'prompt': 'Hardware',
    },
    'timer': {
        'prompt': 'Transponders:',
        'hint': 'Transponder decoder spec TYPE:ADDR, eg: rrs:10.1.2.3',
        'defer': True,
        'attr': 'timer',
    },
    'alttimer': {
        'prompt': 'Impulse:',
        'hint': 'Impulse timer port eg: /dev/ttyS0',
        'defer': True,
        'attr': 'alttimer'
    },
    'secexp': {
        'control': 'section',
        'prompt': 'Export',
    },
    'mirrorcmd': {
        'prompt': 'Command:',
        'hint': 'Command to run if export script is enabled',
        'attr': 'mirrorcmd',
    },
    'mirrorpath': {
        'prompt': 'Path:',
        'hint': 'Result export path',
        'attr': 'mirrorpath',
    },
    'mirrorfile': {
        'prompt': 'Filename:',
        'hint': 'Result export filename prefix',
        'attr': 'mirrorfile',
    },
    'shortname': {
        'prompt': 'Short Name:',
        'hint': 'Short meet name on web export header',
        'attr': 'shortname',
    },
    'eventcode': {
        'prompt': 'Event Code:',
        'hint': 'Event code saved in reports',
        'attr': 'eventcode',
    },
    'resfiles': {
        'prompt': 'Result Files:',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Build results on export?',
        'hint': 'Build result files with export',
        'attr': 'resfiles',
        'default': True,
    },
    'resarrival': {
        'prompt': '',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Include arrivals?',
        'hint': 'Include arrivals on result export',
        'attr': 'resarrival',
        'default': False,
    },
    'resdetail': {
        'prompt': '',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Include lap/split times?',
        'hint': 'Include lap/split time detail with result export',
        'attr': 'resdetail',
        'default': True,
    },
    'lifexport': {
        'prompt': 'LIF Export:',
        'control': 'check',
        'type': 'bool',
        'subtext': 'Build LIF file on export?',
        'hint': 'Export LIF result file with results',
        'attr': 'lifexport',
        'default': False,
    },
    # the following are currently used for html export, but are likely
    # to be removed in later versions
    'linkbase': {
        'attr': 'linkbase',
        'control': 'none',
        'default': '.',
    },
    'indexlink': {
        'attr': 'indexlink',
        'control': 'none',
    },
    'prevlink': {
        'attr': 'prevlink',
        'control': 'none',
    },
    'nextlink': {
        'attr': 'nextlink',
        'control': 'none',
    },
}


def mkdevice(portstr=None, curdev=None):
    """Return a decoder handle for the provided port specification."""
    # Note: If possible, returns the current device
    if portstr is None:
        portstr = ''
    ret = curdev
    devtype = 'null'
    if metarace.sysconf.has_option('decoder', 'default'):
        devtype = metarace.sysconf.get('decoder', 'default')
        _log.debug('Default type set to %s from sysconf', devtype)
    (a, b, c) = portstr.partition(':')
    if b:
        a = a.lower()
        if a in _HANDLERS:
            devtype = a
        a = c  # shift port into a
    devport = a
    if curdev is None:
        curdev = _HANDLERS[devtype]()
        curdev.setport(devport)
    elif type(curdev) is _HANDLERS[devtype]:
        _log.debug('Requested decoder is %s', curdev.__class__.__name__)
        curdev.setport(devport)
    else:
        _log.debug('Changing decoder type from %s to %s',
                   curdev.__class__.__name__, devtype)
        curdev.setcb(None)
        wasalive = curdev.running()
        if wasalive:
            curdev.exit('Change decoder type')
        curdev = None
        curdev = _HANDLERS[devtype]()
        curdev.setport(devport)
        _log.debug('Starting %s decoder', curdev.__class__.__name__)
        if wasalive:
            curdev.start()
    return curdev


class roadmeet:
    """Road meet application class."""

    ## Meet Menu Callbacks
    def menu_meet_save_cb(self, menuitem, data=None):
        """Save current all meet data to config."""
        self.saveconfig()

    def get_short_name(self):
        """Return the <= 16 char shortname."""
        return self.shortname

    def cat_but_auto_clicked(self, but, entry, data=None):
        """Lookup cats and write them into the supplied entry."""
        entry.set_text(' '.join(self.rdb.listcats()))

    def menu_event_decisions_activate_cb(self, menuitem, data=None):
        """Edit decisions of the commissaires panel."""
        if self.curevent is not None:
            self.curevent.decisions = uiutil.decisions_dlg(
                self.window, self.curevent.decisions)

    def menu_event_properties_activate_cb(self, menuitem, data=None):
        """Edit event specific properties."""
        if self.curevent is not None:
            _log.debug('Editing event properties')
            if self.curevent.edit_event_properties(self.window):
                _log.info('Event re-start required')
                self.event_reload()

    def menu_event_reset_cb(self, menuitem, data=None):
        """Reset current event."""
        if self.curevent is not None:
            _log.debug('Reset event')
            if uiutil.questiondlg(
                    window=self.window,
                    question='Reset event to idle?',
                    subtext='Note: All result and timing data will be cleared.',
                    title='Reset Event?'):
                self.curevent.resettimer()
                _log.info('Reset event to idle')

    def menu_meet_properties_cb(self, menuitem, data=None):
        """Edit meet properties."""
        metarace.sysconf.add_section('export', _EXPORT_SCHEMA)
        metarace.sysconf.add_section('telegraph', _TG_SCHEMA)
        metarace.sysconf.add_section('thbc', _THBC_SCHEMA)
        metarace.sysconf.add_section('rru', _RRU_SCHEMA)
        metarace.sysconf.add_section('rrs', _RRS_SCHEMA)
        metarace.sysconf.add_section('timy', _TIMY_SCHEMA)
        cfgres = uiutil.options_dlg(window=self.window,
                                    title='Meet Properties',
                                    sections={
                                        'meet': {
                                            'title': 'Meet',
                                            'schema': _CONFIG_SCHEMA,
                                            'object': self,
                                        },
                                        'export': {
                                            'title': 'Export',
                                            'schema': _EXPORT_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                        'telegraph': {
                                            'title': 'Telegraph',
                                            'schema': _TG_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                        'timy': {
                                            'title': 'Timy',
                                            'schema': _TIMY_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                        'thbc': {
                                            'title': 'THBC',
                                            'schema': _THBC_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                        'rru': {
                                            'title': 'RR USB',
                                            'schema': _RRU_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                        'rrs': {
                                            'title': 'RR System',
                                            'schema': _RRS_SCHEMA,
                                            'object': metarace.sysconf,
                                        },
                                    })

        # check for sysconf changes:
        syschange = False
        timychg = False
        timerchg = False
        tgchg = False
        for sec in ('export', 'timy', 'rru', 'rrs', 'telegraph', 'thbc'):
            for key in cfgres[sec]:
                if cfgres[sec][key][0]:
                    syschange = True
                    if sec == 'telegraph':
                        tgchg = True
                    elif sec in ('rru', 'rrs', 'thbc'):
                        timerchg = True
                    elif sec == 'timy':
                        timerchg = True
                        timychg = True
        if syschange:
            _log.info('Saving config updates to meet folder')
            with metarace.savefile(metarace.SYSCONF, perm=0o600) as f:
                metarace.sysconf.write(f)

        # reset telegraph connection if required
        if tgchg:
            _log.info('Re-start telegraph')
            newannounce = telegraph()
            newannounce.setcb(self._controlcb)
            newannounce.start()
            oldannounce = self.announce
            self.announce = newannounce
            oldannounce.exit()

        # reset alttimer connection if required
        if timychg:
            _log.info('Re-start alt timer')
            newtimy = timy()
            newtimy.setcb(self._alttimercb)
            newtimy.start()
            oldtimy = self._alttimer
            self._alttimer = newtimy
            oldtimy.exit()

        res = cfgres['meet']
        # handle a change in announce topic
        if res['anntopic'][0] or tgchg:
            otopic = res['anntopic'][1]
            if otopic:
                self.announce.unsubscribe('/'.join((otopic, 'control', '#')))
            if self.anntopic:
                self.announce.subscribe('/'.join(
                    (self.anntopic, 'control', '#')))

        # handle change in timer topic
        if res['timertopic'][0] or tgchg:
            otopic = res['timertopic'][1]
            if otopic:
                self.announce.unsubscribe(otopic)

        # reset remote option
        if res['timertopic'][0] or res['remoteenable'][0] or tgchg:
            self.remote_reset()

        # if type has changed, backup config and reload
        if res['etype'][0]:
            timerchg = True
            reopen = False
            if self.curevent is not None:
                reopen = True
                conf = self.curevent.configfile
                self.close_event()
                backup = conf + '.bak'
                _log.warning('Event type change, config backed up to %s',
                             backup)
                try:
                    if os.path.exists(backup):
                        os.unlink(backup)
                    os.link(conf, backup)
                except Exception as e:
                    _log.warning('%s saving event backup: %s',
                                 e.__class__.__name__, e)
            if reopen:
                self.open_event()

        # reset timer ports
        if res['timer'][0] or res['alttimer'][0] or timerchg:
            self.menu_timing_reconnect_activate_cb(None)

        self.set_title()

    def report_strings(self, rep):
        """Copy meet information into the supplied report."""
        rep.strings['title'] = self.title
        rep.strings['subtitle'] = self.subtitle
        rep.strings['host'] = self.host
        rep.strings['docstr'] = self.document
        rep.strings['datestr'] = strops.promptstr('Date:', self.date)
        rep.strings['commstr'] = strops.promptstr('PCP:', self.pcp)
        rep.strings['orgstr'] = strops.promptstr('Organiser:', self.organiser)
        diststr = self.diststr
        if not diststr:
            if self.distance:
                diststr = strops.promptstr('Distance:',
                                           '%0.1f\u2006km' % (self.distance))
        rep.strings['diststr'] = diststr
        if self.eventcode:
            rep.eventid = self.eventcode
        if self.prevlink:
            rep.prevlink = self.prevlink
        if self.nextlink:
            rep.nextlink = self.nextlink
        if self.indexlink:
            rep.indexlink = self.indexlink
        if self.shortname:
            rep.shortname = self.shortname

    def print_report(self, sections=[], provisional=False, filename='output'):
        """Print the pre-formatted sections in a standard report."""
        rep = report.report()
        rep.provisional = provisional
        rep.id = filename
        self.report_strings(rep)
        for sec in sections:
            rep.add_section(sec)

        if self.doprint not in ('preview', 'dialog', 'direct'):
            # Save a copy to pdf and xlsx
            ofile = filename + '.pdf'
            with metarace.savefile(ofile, mode='b') as f:
                rep.output_pdf(f)
            ofile = filename + '.xlsx'
            with metarace.savefile(ofile, mode='b') as f:
                rep.output_xlsx(f)
            # Log completion
            _log.info('Saved report to %s.pdf', filename)

        if self.doprint != 'save':
            # report preparation complete, trigger
            method = Gtk.PrintOperationAction.PREVIEW
            if self.doprint == 'dialog':
                method = Gtk.PrintOperationAction.PRINT_DIALOG
            elif self.doprint == 'direct':
                method = Gtk.PrintOperationAction.PRINT
            print_op = Gtk.PrintOperation.new()
            print_op.set_print_settings(self.printprefs)
            print_op.set_default_page_setup(self.pageset)
            print_op.connect('begin_print', self.begin_print, rep)
            print_op.connect('draw_page', self.draw_print_page, rep)
            print_op.connect('done', self.finish_print, rep)
            print_op.set_allow_async(True)
            res = print_op.run(method, self.window)
            if res == Gtk.PrintOperationResult.APPLY:
                self.printprefs = print_op.get_print_settings()
                _log.debug('Updated print preferences')
            elif res == Gtk.PrintOperationResult.IN_PROGRESS:
                _log.debug('Print operation in progress')
            elif res == Gtk.PrintOperationResult.ERROR:
                printerr = print_op.get_error()
                _log.error('Print operation error: %s', printerr.message)
            else:
                _log.error('Print operation cancelled')
            self._print_report_thread = None
            self._print_report_rep = None
        return False

    def finish_print(self, operation, context, rep):
        """Notify print completion."""
        _log.log(report._LOGLEVEL_TEMP, 'Printing %s done.', rep.id)

    def begin_print(self, operation, context, rep):
        """Set print pages and units."""
        _log.log(report._LOGLEVEL_TEMP, 'Printing %s ...', rep.id)
        rep.start_gtkprint(context.get_cairo_context())
        operation.set_use_full_page(True)
        operation.set_n_pages(rep.get_pages())
        operation.set_unit(Gtk.Unit.POINTS)

    def draw_print_page(self, operation, context, page_nr, rep):
        """Draw to the nominated page."""
        rep.set_context(context.get_cairo_context())
        _log.log(report._LOGLEVEL_TEMP, 'Printing %s page %d/%d', rep.id,
                 page_nr + 1, rep.get_pages())
        rep.draw_page(page_nr)

    def menu_meet_quit_cb(self, menuitem, data=None):
        """Quit the application."""
        self.window.close()

    def event_reload(self):
        """Open the event handler."""
        self.open_event()
        self.set_title()
        return False

    def menu_event_armstart_activate_cb(self, menuitem, data=None):
        """Default armstart handler."""
        _log.debug('Arm start request')
        try:
            self.curevent.armstart()
        except Exception as e:
            _log.error('Arm start %s: %s', e.__class__.__name__, e)

    def menu_event_armlap_activate_cb(self, menuitem, data=None):
        """Default armlap handler."""
        _log.debug('Arm lap request')
        try:
            self.curevent.armlap()
        except Exception as e:
            _log.error('Arm lap %s: %s', e.__class__.__name__, e)

    def menu_event_armfin_activate_cb(self, menuitem, data=None):
        """Default armfin handler."""
        _log.debug('Arm finish request')
        try:
            self.curevent.armfinish()
        except Exception as e:
            _log.error('Arm finish %s: %s', e.__class__.__name__, e)

    def menu_event_finished_activate_cb(self, menuitem, data=None):
        """Default finished handler."""
        _log.debug('Set finished request')
        try:
            self.curevent.set_finished()
        except Exception as e:
            _log.error('Set finished %s: %s', e.__class__.__name__, e)

    def open_event(self):
        """Open provided event handle."""
        self.close_event()
        if self.etype not in ROADRACE_TYPES:
            _log.warning('Unknown event type %r', self.etype)
        if self.etype == 'irtt':
            self.curevent = irtt(self, self.etype, True)
        elif self.etype == 'trtt':
            self.curevent = trtt(self, self.etype, True)
        else:
            self.curevent = rms(self, self.etype, True)

        self.curevent.loadconfig()
        self.event_box.add(self.curevent.frame)

        # re-populate the rider command model.
        cmdo = self.curevent.get_ridercmdorder()
        cmds = self.curevent.get_ridercmds()
        if cmds is not None:
            self.action_model.clear()
            for cmd in cmdo:
                self.action_model.append([cmd, cmds[cmd]])
            self.action_combo.set_active(0)
        self.curevent.show()

    def close_event(self):
        """Close the currently opened event."""
        if self.curevent is not None:
            if self.curevent.frame in self.event_box.get_children():
                self.event_box.remove(self.curevent.frame)
            self.curevent.destroy()
            self.curevent = None
            self.stat_but.update('idle', 'Closed')
            self.stat_but.set_sensitive(False)

    ## Reports menu callbacks.
    def menu_reports_startlist_activate_cb(self, menuitem, data=None):
        """Generate a startlist."""
        if self.curevent is not None:
            sections = self.curevent.startlist_report()
            if not sections:
                _log.warning('Empty startlist')
            self.print_report(sections,
                              provisional=self.provisionalstart,
                              filename='startlist')

    def menu_reports_callup_activate_cb(self, menuitem, data=None):
        """Generate a start line call-up."""
        if self.curevent is not None:
            sections = self.curevent.callup_report()
            if not sections:
                _log.warning('Empty callup')
            self.print_report(sections,
                              provisional=self.provisionalstart,
                              filename='callup')

    def menu_reports_collect_activate_cb(self, menuitem, data=None):
        """Generate a number collection sheet."""
        if self.curevent is not None:
            sections = self.numbercollect_report()
            if not sections:
                _log.warning('Empty collect')
            self.print_report(sections, filename='numbercollection')

    def numbercollect_report(self):
        """Return a number collection/allocation report"""
        sec = report.twocol_startlist('numbercollect')
        sec.heading = 'Number Collection'
        sec.grey = True
        aux = []
        # add all riders, but mark those not in race
        for rid, dbr in self.rdb.items():
            cnt = 0
            if dbr['series'] not in ('spare', 'cat', 'team', 'ds', 'series'):
                namekey = ''.join(
                    (dbr['last'].lower(), dbr['first'].lower()[0:2]))
                aux.append((namekey, cnt, dbr))
                cnt += 1
        if aux:
            aux.sort()
            for r in aux:
                dbr = r[2]
                scratch = self.curevent.getrider(dbr['no'],
                                                 dbr['series']) is None
                sec.lines.append((dbr['no'], None, dbr.regname(),
                                  dbr.primary_cat(), None, None, scratch))
        return (sec, )

    def menu_reports_signon_activate_cb(self, menuitem, data=None):
        """Generate a sign on sheet."""
        if self.curevent is not None:
            sections = self.curevent.signon_report()
            if not sections:
                _log.warning('Empty signon')
            self.print_report(sections, filename='signonsheet')

    def menu_reports_analysis_activate_cb(self, menuitem, data=None):
        """Generate the analysis report."""
        if self.curevent is not None:
            sections = self.curevent.analysis_report()
            if not sections:
                _log.warning('Empty analysis')
            self.print_report(sections, filename='analysisreport')

    def menu_reports_camera_activate_cb(self, menuitem, data=None):
        """Generate the camera operator report."""
        if self.curevent is not None:
            sections = self.curevent.camera_report()
            if not sections:
                _log.warning('Empty camera report')
            self.print_report(sections, filename='camerareport')

    def event_results_points_activate_cb(self, menuitem, data=None):
        """Generate the points tally report."""
        if self.curevent is not None:
            sections = self.curevent.points_report()
            if not sections:
                _log.warning('Empty points report')
            self.print_report(sections, filename='pointstally')

    def menu_reports_result_activate_cb(self, menuitem, data=None):
        """Generate the event result report."""
        if self.curevent is not None:
            sections = self.curevent.result_report()
            if not sections:
                _log.warning('Empty result report')
            self.print_report(sections,
                              self.curevent.timerstat != 'finished',
                              filename='result')

    def menu_data_replace_activate_cb(self, menuitem, data=None):
        """Replace rider db from disk."""
        if not uiutil.questiondlg(
                window=self.window,
                question='Replace all rider, team and category entries?',
                title='Replace riderdb?'):
            _log.debug('Replace riders cancelled')
            return False
        sfile = uiutil.chooseCsvFile(title='Select rider file to load from',
                                     parent=self.window,
                                     path='.')
        if sfile is not None:
            try:
                self.rdb.clear(notify=False)
                count = self.rdb.load(sfile)
                _log.info('Loaded %d entries from %s', count, sfile)
            except Exception as e:
                _log.error('%s loading riders: %s', e.__class__.__name__, e)
        else:
            _log.debug('Replace riders cancelled')

    def menu_data_clear_activate_cb(self, menuitem, data=None):
        """Clear rider db."""
        self.rdb.clear()
        _log.info('Cleared rider db')

    def menu_import_riders_activate_cb(self, menuitem, data=None):
        """Add riders to database."""
        sfile = uiutil.chooseCsvFile(title='Select rider file to import',
                                     parent=self.window,
                                     path='.')
        if sfile is not None:
            try:
                count = self.rdb.load(sfile, overwrite=True)
                _log.info('Imported %d entries from %s', count, sfile)
            except Exception as e:
                _log.error('%s importing: %s', e.__class__.__name__, e)
        else:
            _log.debug('Import riders cancelled')

    def menu_import_chipfile_activate_cb(self, menuitem, data=None):
        """Import a transponder chipfile."""
        sfile = uiutil.chooseCsvFile(title='Select chipfile to import',
                                     parent=self.window,
                                     path='.')
        if sfile is not None:
            try:
                count = self.rdb.load_chipfile(sfile)
                _log.info('Imported %d refids from chipfile %s', count, sfile)
            except Exception as e:
                _log.error('%s importing chipfile: %s', e.__class__.__name__,
                           e)
        else:
            _log.debug('Import chipfile cancelled')

    def menu_import_startlist_activate_cb(self, menuitem, data=None):
        """Import a startlist."""
        if self.curevent is None:
            _log.info('No event open for starters import')
            return
        sfile = uiutil.chooseCsvFile(title='Select startlist file to import',
                                     parent=self.window,
                                     path='.')
        self.import_starters(sfile)

    def import_starters(self, sfile):
        """Import starters from the nominated csvfile"""
        if os.path.isfile(sfile):
            count = 0
            with open(sfile, encoding='utf-8', errors='replace') as f:
                cr = csv.reader(f)
                for r in cr:
                    if len(r) > 1 and r[1].isalnum() and r[1].lower() not in (
                            'no', 'no.'):
                        bib = r[1].strip().lower()
                        series = ''
                        if len(r) > 2:
                            series = r[2].strip()
                        self.curevent.addrider(bib, series)
                        start = tod.mktod(r[0])
                        if start is not None:
                            self.curevent.starttime(start, bib, series)
                        count += 1
            _log.info('Imported %d starters from %s', count, sfile)
        else:
            _log.debug('Import startlist cancelled')

    def menu_export_riders_activate_cb(self, menuitem, data=None):
        """Export rider database."""
        sfile = uiutil.chooseCsvFile(title='Select file to export riders to',
                                     mode=Gtk.FileChooserAction.SAVE,
                                     parent=self.window,
                                     hintfile='riders_export.csv',
                                     path='.')
        if sfile is not None:
            try:
                self.rdb.save(sfile)
                _log.info('Export rider data to %s', sfile)
            except Exception as e:
                _log.error('%s exporting riders: %s', e.__class__.__name__, e)
        else:
            _log.debug('Export rider data cancelled')

    def menu_export_chipfile_activate_cb(self, menuitem, data=None):
        """Export transponder chipfile from rider model."""
        sfile = uiutil.chooseCsvFile(title='Select file to export refids to',
                                     mode=Gtk.FileChooserAction.SAVE,
                                     parent=self.window,
                                     hintfile='chipfile.csv',
                                     path='.')
        if sfile is not None:
            try:
                count = self.rdb.save_chipfile(sfile)
                _log.info('Exported %d refids to chipfile %s', count, sfile)
            except Exception as e:
                _log.error('%s exporting chipfile: %s', e.__class__.__name__,
                           e)
        else:
            _log.debug('Export chipfile cancelled')

    def menu_export_result_activate_cb(self, menuitem, data=None):
        """Export raw result to disk."""
        if self.curevent is None:
            _log.info('No event open')
            return

        rfilename = uiutil.chooseCsvFile(
            title='Select file to save results to.',
            mode=Gtk.FileChooserAction.SAVE,
            parent=self.window,
            hintfile='results.csv',
            path='.')
        if rfilename is not None:
            with metarace.savefile(rfilename) as f:
                cw = csv.writer(f)
                cw.writerow(['Rank', 'No.', 'Time', 'Bonus', 'Penalty'])
                for r in self.curevent.result_gen(''):
                    opr = ['', '', '', '', '']
                    for i in range(0, 2):
                        if r[i]:
                            opr[i] = str(r[i])
                    for i in range(2, 5):
                        if r[i]:
                            opr[i] = str(r[i].timeval)
                    cw.writerow(opr)
            _log.info('Export result to %s', rfilename)

    def menu_export_startlist_activate_cb(self, menuitem, data=None):
        """Extract startlist from current event."""
        if self.curevent is None:
            _log.info('No event open')
            return

        rfilename = uiutil.chooseCsvFile(
            title='Select file to save startlist to.',
            mode=Gtk.FileChooserAction.SAVE,
            parent=self.window,
            hintfile='startlist.csv',
            path='.')
        if rfilename is not None:
            with metarace.savefile(rfilename) as f:
                cw = csv.writer(f)
                cw.writerow(['Start', 'No.', 'Series', 'Name', 'Cat'])
                if self.etype == 'irtt':
                    for r in self.curevent.startlist_gen():
                        cw.writerow(r)
                else:
                    clist = self.curevent.get_catlist()
                    clist.append('')
                    for c in clist:
                        for r in self.curevent.startlist_gen(c):
                            cw.writerow(r)

            _log.info('Export startlist to %s', rfilename)
        else:
            _log.info('Export startlist cancelled')

    def _run_export_thread(self, srep=None, frep=None):
        """Output report versions and start a mirror process"""

        # Announce JSON if enabled
        if frep is not None and self.announceresult:
            _log.debug('Announce result')
            self.obj_announce(command='result', obj=frep.serialise())

        # Output files if required
        for r in (srep, frep):
            if r is not None:
                _log.debug('Writing out report %s', r.id)
                lb = os.path.join(self.linkbase, r.id)
                lt = ['pdf', 'xlsx']
                r.canonical = '.'.join([lb, 'json'])
                ofile = os.path.join(self.exportpath, r.id + '.pdf')
                with metarace.savefile(ofile, mode='b') as f:
                    r.output_pdf(f)
                ofile = os.path.join(self.exportpath, r.id + '.xlsx')
                with metarace.savefile(ofile, mode='b') as f:
                    r.output_xlsx(f)
                ofile = os.path.join(self.exportpath, r.id + '.json')
                with metarace.savefile(ofile) as f:
                    r.output_json(f)
                ofile = os.path.join(self.exportpath, r.id + '.html')
                with metarace.savefile(ofile) as f:
                    r.output_html(f, linkbase=lb, linktypes=lt)

        # run and await export mirror
        if self.mirrorpath or self.mirrorcmd:
            mt = mirror(localpath=os.path.join(EXPORTPATH, ''),
                        remotepath=self.mirrorpath,
                        mirrorcmd=self.mirrorcmd)
            mt.start()
            mt.join()
        _log.debug('Export thread[%s] complete', self._export_thread.native_id)
        return False

    def menu_data_results_cb(self, menuitem, data=None):
        """Create result report and/or export"""

        # abort if no event present
        if self.curevent is None:
            return False

        if not self._export_lock.acquire(False):
            _log.info('Export in progress')
            return False
        try:
            if self._export_thread is not None:
                if not self._export_thread.is_alive():
                    _log.debug('Stale exporter handle removed')
                    self._export_thread = None
                else:
                    _log.info('Export in progress')
                    return False

            if self.lifexport:  # save current lif with export
                lifdat = self.curevent.lifexport()
                if len(lifdat) > 0:
                    liffile = os.path.join(self.exportpath, 'lifexport.lif')
                    with metarace.savefile(liffile) as f:
                        cw = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                        for r in lifdat:
                            cw.writerow(r)

            srep = None
            frep = None
            if self.resfiles or self.announceresult:
                _log.debug('Building start/finish reports')
                if self.mirrorfile:
                    filebase = self.mirrorfile
                else:
                    filebase = '.'
                if filebase in ('', '.'):
                    filebase = ''
                    if self.resfiles:
                        _log.warn('Using default filenames for export')
                else:
                    pass

                fnv = []
                if filebase:
                    fnv.append(filebase)
                fnv.append('startlist')
                sfile = '_'.join(fnv)
                fnv[-1] = 'result'
                ffile = '_'.join(fnv)

                # Include startlist unless event finished
                if self.resfiles and self.curevent.timerstat != 'finished':
                    filename = sfile
                    srep = report.report()
                    srep.id = filename
                    self.report_strings(srep)
                    if self.provisionalstart:
                        srep.set_provisional(True)
                    if self.indexlink:
                        srep.indexlink = self.indexlink
                    if self.prevlink:
                        srep.prevlink = '_'.join((self.prevlink, 'startlist'))
                    if self.nextlink:
                        srep.nextlink = '_'.join((self.nextlink, 'startlist'))
                    srep.resultlink = ffile
                    if self.etype in ('irtt', 'cross', 'trtt'):
                        for sec in self.curevent.callup_report():
                            srep.add_section(sec)
                    else:
                        for sec in self.curevent.startlist_report():
                            srep.add_section(sec)
                    _log.debug('Startlist report built')

                # Then export a result
                frep = report.report()
                self.report_strings(frep)

                # Collect result sections
                ressecs = self.curevent.result_report()

                # Set provisional status
                if self.curevent.timerstat != 'finished':
                    frep.set_provisional(True)
                    # include arrivals if configured
                    if self.resarrival:
                        for sec in self.curevent.arrival_report():
                            frep.add_section(sec)
                else:
                    frep.reportstatus = 'final'

                # Add results to body of report
                for sec in ressecs:
                    frep.add_section(sec)

                # Include result details if configured
                if self.resdetail:
                    for sec in self.curevent.analysis_report():
                        frep.add_section(sec)

                filename = ffile
                frep.id = filename
                frep.startlink = sfile
                if self.indexlink:
                    frep.indexlink = self.indexlink
                if self.prevlink:
                    frep.prevlink = '_'.join((self.prevlink, 'result'))
                if self.nextlink:
                    frep.nextlink = '_'.join((self.nextlink, 'result'))
                lb = os.path.join(self.linkbase, filename)
                lt = ['pdf', 'xlsx']
                frep.canonical = '.'.join([lb, 'json'])
                _log.debug('Result report built')

            # Bottom half - write to disk and export
            self._export_thread = threading.Thread(
                target=self._run_export_thread,
                name='export',
                args=(srep, frep),
                daemon=True,
            )
            self._export_thread.start()
            _log.debug('Started export thread[%s]',
                       self._export_thread.native_id)
        except Exception as e:
            _log.error('%s starting export: %s', e.__class__.__name__, e)
        finally:
            self._export_lock.release()
        return False

    ## Timing menu callbacks
    def menu_timing_status_cb(self, menuitem, data=None):
        if self.timer:
            if self._timer.connected():
                _log.info('Request timer status')
                self._timer.status()
            else:
                _log.info('Decoder disconnected')
        else:
            _log.info('No decoder configured')
        # always call into alt timer
        self._alttimer.status()

    def menu_timing_start_activate_cb(self, menuitem, data=None):
        """Manually set event start/elapsed time via trigger."""
        if self.curevent is None:
            _log.info('No event open to set elapsed time on')
        else:
            self.curevent.elapsed_dlg()

    def entry_set_now(self, button, entry=None):
        """Enter the current time in the provided entry."""
        entry.set_text(tod.now().timestr())
        entry.activate()

    def menu_timing_recalc(self, entry, ste, fte, nte):
        """Update the net time entry for the supplied start and finish."""
        st = tod.mktod(ste.get_text())
        ft = tod.mktod(fte.get_text())
        if st is not None and ft is not None:
            ste.set_text(st.timestr())
            fte.set_text(ft.timestr())
            nte.set_text((ft - st).timestr())

    def menu_timing_clear_activate_cb(self, menuitem, data=None):
        """Start a new timing session in attached timers"""
        # Note: clear will perform reset, stop_session, clear,
        # sync, and start_session in whatever order is appropriate
        # for the decoder type
        self._timer.clear()
        self._alttimer.clrmem()

    def set_altchannels(self):
        self._alttimer.armlock()  # lock the arm to capture all hits
        self._alttimer.arm(0)  # start line
        self._alttimer.arm(1)  # finish line (primary)
        self._alttimer.dearm(6)
        self._alttimer.dearm(7)
        self._alttimer.dearm(8)
        if self.etype == 'irtt':
            self._alttimer.write('DTS01.00')
            self._alttimer.write('DTF00.01')
            self._alttimer.arm(2)  # finish line (photo cell)
            self._alttimer.arm(3)  # finish line (plunger)
            self._alttimer.arm(4)  # start line (backup)
            self._alttimer.arm(5)  # spare
        else:
            self._alttimer.write('DTS00.01')
            if self.etype == 'trtt':
                self._alttimer.write('DTF00.01')
            else:
                # assume 1 second gaps at finish for road types
                self._alttimer.write('DTF01.00')
            self._alttimer.dearm(2)
            self._alttimer.dearm(3)
            self._alttimer.dearm(4)
            self._alttimer.dearm(5)

    def menu_timing_reconnect_activate_cb(self, menuitem, data=None):
        """Drop current timer connection and re-connect"""
        self.set_timer(self.timer, force=True)
        self._alttimer.setport(self.alttimer)
        self._alttimer.sane()
        self.set_altchannels()
        _log.info('Re-connect/re-start attached timers')

    def restart_decoder(self, data=None):
        """Request re-start of decoder."""
        self._timer.start_session()
        return None

    def menu_timing_configure_activate_cb(self, menuitem, data=None):
        """Attempt to re-configure the attached decoder from saved config."""
        if self._timer.__class__.__name__ == 'thbc':
            if not self._timer.connected():
                _log.info('Timer not connected, config not possible')
                return False
            if not uiutil.questiondlg(
                    window=self.window,
                    question='Re-configure THBC Decoder IP Settings?',
                    subtext=
                    'Note: Passings will not be captured while decoder is updating.',
                    title='Update Decoder IP?'):
                _log.debug('Config aborted')
                return False
            self._timer.stop_session()
            self._timer.sane()
            GLib.timeout_add_seconds(60, self.restart_decoder)
            self._timer.ipconfig()
        else:
            _log.info('Decoder config not available')
        return None

    ## Help menu callbacks
    def menu_help_about_cb(self, menuitem, data=None):
        """Display metarace about dialog."""
        uiutil.about_dlg(self.window, __version__)

    ## Race Control Elem callbacks
    def event_stat_but_clicked_cb(self, button, data=None):
        """Call through into event if open."""
        if self.curevent is not None:
            self.curevent.stat_but_clicked(button)

    def event_stat_entry_activate_cb(self, entry, data=None):
        """Pass the chosen action and bib list through to curevent."""
        action = self.action_model.get_value(
            self.action_combo.get_active_iter(), 0)
        if self.curevent is not None:
            if self.curevent.event_ctrl(action, self.action_entry.get_text()):
                self.action_entry.set_text('')

    ## Menu button callbacks
    def event_action_combo_changed_cb(self, combo, data=None):
        """Notify curevent of change in combo."""
        aiter = self.action_combo.get_active_iter()
        if self.curevent is not None and aiter is not None:
            action = self.action_model.get_value(aiter, 0)
            self.curevent.ctrl_change(action, self.action_entry)

    def menu_clock_clicked_cb(self, button, data=None):
        """Handle click on menubar clock."""
        _log.info('PC ToD: %s', tod.now().rawtime())

    ## 'Slow' Timer callback - this is the main ui event routine
    def timeout(self):
        """Update status buttons and time of day clock button."""
        try:
            if self.running:
                # call into event timeout handler
                if self.curevent is not None:
                    self.curevent.timeout()

                # update the menu status button
                nt = tod.now().meridiem()
                if self.rfuact:
                    self.rfustat.update('activity', nt)
                else:
                    if self.timer:
                        if self._timer.connected():
                            self.rfustat.update('ok', nt)
                        else:
                            self.rfustat.update('error', nt)
                    else:
                        self.rfustat.update('idle', nt)
                self.rfuact = False

                # attempt to heal a broken link
                if self.timer:
                    if self._timer.connected():
                        self.rfufail = 0
                    else:
                        self.rfufail += 1
                        if self.rfufail > 20:
                            self.rfufail = 0
                            eport = self.timer.split(':', 1)[-1]
                            self._timer.setport(eport)
                else:
                    self.rfufail = 0

                # purge status line
                self.statusHandler.purge()
            else:
                return False
        except Exception as e:
            _log.critical('%s in meet timeout: %s', e.__class__.__name__, e)
        return True

    ## Window methods
    def set_title(self, extra=''):
        """Update window title from meet properties."""
        tv = []
        if self.etype in ROADRACE_TYPES:
            tv.append(ROADRACE_TYPES[self.etype] + ':')

        title = self.title.strip()
        if title:
            tv.append(title)
        subtitle = self.subtitle.strip()
        if subtitle:
            tv.append(subtitle)
        self.window.set_title(' '.join(tv))
        if self.curevent is not None:
            self.curevent.set_titlestr(subtitle)

    def meet_destroy_cb(self, window, msg=''):
        """Handle destroy signal and exit application."""
        rootlogger = logging.getLogger()
        rootlogger.removeHandler(self.statusHandler)
        rootlogger.removeHandler(self.logHandler)
        #self.window.hide()
        GLib.idle_add(self.meet_destroy_handler)

    def meet_destroy_handler(self):
        if self.curevent is not None:
            self.close_event()
        if self.started:
            self.saveconfig()
            self.shutdown()  # threads are joined in shutdown
        rootlogger = logging.getLogger()
        if self.loghandler is not None:
            rootlogger.removeHandler(self.loghandler)
        self.running = False
        Gtk.main_quit()
        return False

    def key_event(self, widget, event):
        """Collect key events on main window and send to event."""
        if event.type == Gdk.EventType.KEY_PRESS:
            key = Gdk.keyval_name(event.keyval) or 'None'
            if event.state & Gdk.ModifierType.CONTROL_MASK:
                key = key.lower()
                t = tod.now(chan='MAN', refid=str(key))
                if key in ('0', '1'):
                    # trigger
                    t.refid = ''
                    t.chan = strops.id2chan(strops.chan2id(key))
                    self._alttimercb(t)
                    return True
                elif key in ('2', '3', '4', '5', '6', '7', '8', '9'):
                    # passing
                    self._timercb(t)
                    return True
                elif key == 'left':
                    self.notebook.prev_page()
                elif key == 'right':
                    self.notebook.next_page()
            if self.curevent is not None:
                return self.curevent.key_event(widget, event)
        return False

    def shutdown(self, msg=''):
        """Shutdown worker threads and close application."""
        self.started = False
        self.announce.exit(msg)
        self._timer.exit(msg)
        self._alttimer.exit(msg)
        _log.info('Waiting for workers')
        if self._export_thread is not None:
            _log.debug('Result export')
            self._export_thread.join()
            self._export_thread = None
        _log.debug('Telegraph/announce')
        self.announce.join()

    def start(self):
        """Start the timer and rfu threads."""
        if not self.started:
            _log.debug('Meet startup')
            self.announce.start()
            self._timer.start()
            self._alttimer.start()
            self.started = True

    ## Roadmeet functions
    def saveconfig(self):
        """Save current meet data to disk."""
        if self.curevent is not None and self.curevent.winopen:
            self.curevent.saveconfig()
        cw = jsonconfig.config()
        cw.add_section('roadmeet', _CONFIG_SCHEMA)
        cw.import_section('roadmeet', self)
        cw.set('roadmeet', 'id', ROADMEET_ID)
        with metarace.savefile(CONFIGFILE) as f:
            cw.write(f)
        self.rdb.save('riders.csv')
        _log.info('Meet configuration saved')

    def set_timer(self, newdevice='', force=False):
        """Re-set the main timer device and connect callback."""
        if newdevice != self.timer or force:
            self._timer = mkdevice(newdevice, self._timer)
            self.timer = newdevice
        else:
            _log.debug('set_timer - No change required')
        self._timer.setcb(self._timercb)

    def loadconfig(self):
        """Load meet config from disk."""
        cr = jsonconfig.config()
        cr.add_section('roadmeet', _CONFIG_SCHEMA)

        # re-set main log file
        _log.debug('Adding meet logfile handler %r', LOGFILE)
        rootlogger = logging.getLogger()
        if self.loghandler is not None:
            rootlogger.removeHandler(self.loghandler)
            self.loghandler.close()
            self.loghandler = None
        self.loghandler = logging.FileHandler(LOGFILE)
        self.loghandler.setLevel(LOGFILE_LEVEL)
        self.loghandler.setFormatter(logging.Formatter(metarace.LOGFILEFORMAT))
        rootlogger.addHandler(self.loghandler)

        cr.merge(metarace.sysconf, 'roadmeet')
        cr.load(CONFIGFILE)

        # Is this meet path an existing trackmeet?
        if cr.has_section('trackmeet'):
            _log.error('Meet folder contains track meet configuration')
            if not os.isatty(sys.stdout.fileno()):
                uiutil.messagedlg(
                    message='Invalid meet type.',
                    title='Roadmeet: Error',
                    subtext=
                    'Selected meet folder contains configuration for a track meet.'
                )
            sys.exit(-1)

        # Load schema options into meet object
        cr.export_section('roadmeet', self)

        # update hardware ports and telegraph setting
        self.set_timer(self.timer, force=True)
        if self.alttimer:
            self._alttimer.setport(self.alttimer)
            self._alttimer.sane()
            self.set_altchannels()
        if self.anntopic:
            self.announce.subscribe('/'.join((self.anntopic, 'control', '#')))
        self.remote_reset()

        # Re-Initialise rider database
        self.rdb.clear(notify=False)
        _log.debug('meet load riders from riders.csv')
        self.rdb.load('riders.csv')

        # Open the event
        self.open_event()
        self.set_title()

        # make sure export path exists
        if not os.path.exists(self.exportpath):
            os.mkdir(self.exportpath)
            _log.info('Created export path: %r', self.exportpath)

        # check and warn of config mismatch
        cid = cr.get_value('roadmeet', 'id')
        if cid is not None and cid != ROADMEET_ID:
            _log.warning('Meet config mismatch: %r != %r', cid, ROADMEET_ID)

    def get_distance(self):
        """Return meet distance in km."""
        return self.distance

    ## Announcer methods (replaces old irc/unt telegraph)
    def cmd_announce(self, command, msg):
        """Announce the supplied message to the command topic."""
        if self.anntopic:
            topic = '/'.join((self.anntopic, command))
            self.announce.publish(msg, topic)

    def obj_announce(self, command, obj):
        """Publish obj to command as JSON"""
        if self.anntopic:
            topic = '/'.join((self.anntopic, command))
            self.announce.publish_json(obj,
                                       topic,
                                       cls=jsonconfig._configEncoder)

    def rider_announce(self, rvec, command='rider'):
        """Issue a serialised rider vector to announcer."""
        # Deprecated UNT-style list
        self.cmd_announce(command, '\x1f'.join(rvec))

    def timer_announce(self, evt, timer=None, source=''):
        """Send message into announce for remote control."""
        if not self.remoteenable and self.timertopic is not None:
            if timer is None:
                timer = self._timer
            prec = 4
            if timer is self._timer:
                prec = 3  # transponders have reduced precision
            elif 'M' in evt.chan:
                prec = 3
            if evt.source is not None:
                source = evt.source
            tvec = (evt.index, source, evt.chan, evt.refid, evt.rawtime(prec),
                    '')
            self.announce.publish(';'.join(tvec), self.timertopic)
        self.rfustat.update('activity')
        self.rfuact = True
        return False

    def remote_reset(self):
        """Reset remote input of timer messages."""
        _log.debug('Remote control reset')
        if self.timertopic is not None:
            if self.remoteenable:
                _log.debug('Listening for remote timer at %r', self.timertopic)
                self.announce.subscribe(self.timertopic)
            else:
                _log.debug('Remote timer disabled')
                self.announce.unsubscribe(self.timertopic)
        else:
            _log.debug('Remote timer topic not cofigured')

    def remote_timer(self, msg):
        """Process and dispatch a remote timer message."""
        # 'INDEX;SOURCE;CHANNEL;REFID;TIMEOFDAY;DATE'
        tv = msg.split(';')
        if len(tv) == 5 or len(tv) == 6:
            try:
                if len(tv) > 5:
                    # check date against today
                    # if today != tv[5]:
                    # log and return
                    pass
                tval = tod.mktod(tv[4])
                tval.source = tv[1]
                tval.chan = tv[2]
                tval.refid = tv[3]
                _log.debug('Remote src:%r index:%r chan:%r refid:%r @ %r',
                           tv[1], tv[0], tv[2], tv[3], tval.rawtime())
                if 'timy' in tv[1]:
                    tval.index = tv[0]
                    self._alttimercb(tval)
                else:
                    tval.index = 'REM'
                    self._timercb(tval)
            except Exception as e:
                _log.warning('Error reading timer msg %r: %s', msg, e)
        else:
            _log.debug('Invalid remote timer message: %r', tv)

    def remote_command(self, topic, msg):
        """Handle a remote control message."""
        if topic == self.timertopic:
            if self.remoteenable:
                self.remote_timer(msg)
        else:
            _log.debug('Unsupported remote command %r:%r', topic, msg)
        return False

    def getrefid(self, refid):
        """Return a handle to the rider with the suplied refid or None."""
        ret = None
        refid = refid.lower()
        if refid in self._tagmap:
            ret = self.rdb[self._tagmap[refid]]
        elif 'riderno:' in refid:
            rno, rser = strops.bibstr2bibser(refid.split(':')[-1])
            ret = self.rdb.get_rider(rno, rser)
        return ret

    def ridercb(self, rider):
        """Handle a change in the rider model"""
        if rider is not None:
            r = self.rdb[rider]
            summary = r.summary()
            style = 0
            if rider != r.get_id():
                summary = 'Duplicate ' + summary
                style = 2
            series = r['series'].lower()
            if series != 'cat':
                # update refid maps
                otag = None
                ntag = r['refid'].lower()
                if rider in self._maptag:
                    otag = self._maptag[rider]
                if otag != ntag:
                    if rider in self._maptag:
                        del (self._maptag[rider])
                    if otag in self._tagmap:
                        del (self._tagmap[otag])
                    if ntag:
                        self._maptag[rider] = ntag
                        self._tagmap[ntag] = rider
                    _log.debug('Updated tag map %r = %r', ntag, rider)

                # update rider
                for lr in self._rlm:
                    if lr[7] == rider:
                        lr[0] = r.get_bibstr()
                        lr[1] = style
                        lr[2] = r.listname()
                        lr[4] = r['cat']
                        lr[5] = r['refid']
                        lr[6] = htlib.escape(summary)
                        break
                else:
                    lr = [
                        r.get_bibstr(), style,
                        r.listname(), '', r['cat'], r['refid'],
                        htlib.escape(summary), rider
                    ]
                    self._rlm.append(lr)
            else:
                for lr in self._clm:
                    if lr[7] == rider:
                        lr[1] = r['title']
                        lr[2] = r['subtitle']
                        lr[3] = r['footer']
                        lr[4] = r['target']
                        lr[5] = r['distance']
                        lr[6] = r['start']
                        lr[8] = style
                        found = True
                        break
                else:
                    lr = [
                        rider[0], r['title'], r['subtitle'], r['footer'],
                        r['target'], r['distance'], r['start'], rider, style
                    ]
                    self._clm.append(lr)
        else:
            # assume entire map has to be rebuilt
            self._tagmap.clear()
            self._maptag.clear()
            self._rlm.clear()
            self._clm.clear()
            for r in self.rdb:
                dbr = self.rdb[r]
                summary = dbr.summary()
                style = 0
                if r != dbr.get_id():
                    summary = 'Duplicate ' + summary
                    style = 2
                # note: duplicate ids mangle series, so use series from rider
                series = dbr['series'].lower()
                if series != 'cat':
                    refid = dbr['refid'].lower()
                    if refid:
                        self._tagmap[refid] = r
                        self._maptag[r] = refid
                    rlr = [
                        dbr.get_bibstr(), style,
                        dbr.listname(), '', dbr['cat'], dbr['refid'],
                        htlib.escape(summary), r
                    ]
                    self._rlm.append(rlr)
                else:
                    rlr = [
                        r[0], dbr['title'], dbr['subtitle'], dbr['footer'],
                        dbr['target'], dbr['distance'], dbr['start'], r, style
                    ]
                    self._clm.append(rlr)
            _log.debug('Re-built refid tagmap: %d entries', len(self._tagmap))
        if self.curevent is not None:
            self.curevent.ridercb(rider)

    def _timercb(self, evt, data=None):
        """Handle transponder read - in decoder thread."""
        if self.timercb is not None:
            GLib.idle_add(self.timercb, evt)
        GLib.idle_add(self.timer_announce, evt, self._timer, 'rfid')

    def _alttimercb(self, evt, data=None):
        if self.alttimercb is not None:
            GLib.idle_add(self.alttimercb, evt)
        GLib.idle_add(self.timer_announce, evt, self._alttimer, 'timy')

    def _controlcb(self, topic=None, message=None):
        GLib.idle_add(self.remote_command, topic, message)

    def _rcb(self, rider):
        GLib.idle_add(self.ridercb, rider)

    def _catcol_cb(self, cell, path, new_text, col):
        """Callback for editing category info"""
        new_text = new_text.strip()
        self._clm[path][col] = new_text
        cId = self._clm[path][7]
        c = self.rdb[cId]
        cat = c['id']
        if col == 1:
            if new_text != c['title']:
                c['title'] = new_text
        elif col == 2:
            if new_text != c['subtitle']:
                c['subtitle'] = new_text
        elif col == 3:
            if new_text != c['footer']:
                c['footer'] = new_text
        elif col == 4:
            if new_text != c['target']:
                nt = strops.confopt_posint(new_text, '')
                c['target'] = str(nt)
        elif col == 5:
            if new_text != c['distance']:
                nt = strops.confopt_posfloat(new_text, '')
                c['distance'] = str(nt)
        elif col == 6:
            # always re-write start offset to enforce formatting
            nt = tod.mktod(new_text)
            if nt is not None:
                c['start'] = nt.rawtime(0)
            else:
                c['start'] = ''

    def _editname_cb(self, cell, path, new_text, col):
        """Update a rdb by name entry"""
        old_text = self._rlm[path][2]
        if old_text != new_text:
            self._rlm[path][2] = new_text
            dbr = self.rdb[self._rlm[path][7]]
            _log.debug('Updating %s %s detail', dbr.get_label(), dbr.get_id())
            dbr.rename(new_text)

    def _editcol_cb(self, cell, path, new_text, col):
        """Callback for editing categories or transponder ID"""
        new_text = new_text.strip()
        self._rlm[path][col] = new_text
        rId = self._rlm[path][7]
        r = None
        if rId in self.rdb:
            r = self.rdb[rId]
        if r is not None:
            if col == 4:
                if new_text.upper() != r['cat']:
                    r['cat'] = new_text.upper()
            elif col == 5:
                if new_text.lower() != r['refid']:
                    r['refid'] = new_text.lower()

    def _view_button_press(self, view, event):
        """Handle mouse button event on tree view"""
        if event.type == Gdk.EventType.BUTTON_PRESS:
            if event.button == Gdk.BUTTON_SECONDARY:
                self._cur_model = view.get_model()
                pathinfo = view.get_path_at_pos(int(event.x), int(event.y))
                if pathinfo is not None:
                    path, col, cellx, celly = pathinfo
                    view.grab_focus()
                    view.set_cursor(path, col, False)
                    sel = view.get_selection().get_selected()
                    if sel is not None:
                        i = sel[1]
                        r = Gtk.TreeModelRow(self._cur_model, i)
                        self._cur_rider_sel = r[7]
                        self._rider_menu_edit.set_sensitive(True)
                        self._rider_menu_del.set_sensitive(True)
                        self._rider_menu_addevt.set_sensitive(True)
                        self._rider_menu_delevt.set_sensitive(True)
                    else:
                        _log.error('Invalid selection ignored')
                        self._cur_rider_sel = None
                        self._rider_menu_edit.set_sensitive(False)
                        self._rider_menu_del.set_sensitive(False)
                        self._rider_menu_addevt.set_sensitive(False)
                        self._rider_menu_delevt.set_sensitive(False)
                else:
                    self._cur_rider_sel = None
                    self._rider_menu_edit.set_sensitive(False)
                    self._rider_menu_del.set_sensitive(False)
                    self._rider_menu_addevt.set_sensitive(False)
                    self._rider_menu_delevt.set_sensitive(False)
                self._rider_menu.popup_at_pointer(None)
                return True
        return False

    def rider_add_cb(self, menuitem, data=None):
        """Create a new rider entry and edit the content"""
        nser = ''
        if self._cur_model is self._clm:
            nser = 'cat'
        dbr = riderdb.rider(series=nser)
        schema = dbr.get_schema()
        rtype = schema['rtype']['prompt']
        short = 'Create New %s' % (rtype)
        res = uiutil.options_dlg(window=self.window,
                                 title=short,
                                 action=True,
                                 sections={
                                     'rdb': {
                                         'title': 'Rider',
                                         'schema': schema,
                                         'object': dbr,
                                     },
                                 })
        if res['action'] == 0:  # OK
            rider = self.rdb.add_rider(dbr, overwrite=False, notify=False)
            self.ridercb(rider)
            GLib.idle_add(self.select_rider, rider, priority=GLib.PRIORITY_LOW)

    def select_rider(self, rider):
        """Select rider view model if possible"""
        if rider in self.rdb:
            rdb = self.rdb[rider]
            model = self._rlm
            view = self._rlv
            if rdb['series'].lower() == 'cat':
                model = self._clm
                view = self._clv
            found = False
            for r in model:
                if r[7] == rider:
                    view.set_cursor(r.path, None, False)
                    found = True
                    break
            if not found:
                _log.debug('Entry %r not found, unable to select', rider)
        return False

    def rider_edit_cb(self, menuitem, data=None):
        """Edit properties of currently selected entry in riderdb"""
        if self._cur_rider_sel is not None and self._cur_rider_sel in self.rdb:
            doreopen = False
            oldId = self._cur_rider_sel
            dbr = self.rdb[oldId]
            wasDupe = False
            if oldId != dbr.get_id():
                _log.debug('Editing duplicate %r stored as %r', dbr.get_id(),
                           oldId)
                wasDupe = True
            schema = dbr.get_schema()
            label = dbr.get_label()
            short = 'Edit %s %s' % (label, dbr.get_bibstr())
            res = uiutil.options_dlg(window=self.window,
                                     title=short,
                                     action=True,
                                     sections={
                                         'rdb': {
                                             'title': label,
                                             'schema': schema,
                                             'object': dbr,
                                         },
                                     })
            if res['action'] == 0:  # OK
                if res['rdb']['no'][0] or res['rdb']['series'][0]:
                    # Change of number or series
                    self._cur_rider_sel = None  # selected row will be removed
                    backupDbr = None  # save a backup in case rider no exists
                    restoreDbr = None  # restore duplicate if primary avail
                    restoreIdx = None
                    newId = dbr.get_id()

                    # Check for an existing entry with new ID
                    delDest = False  # delete dst from events before adding src
                    if newId in self.rdb:
                        backupDbr = self.rdb[newId]
                        self.rdb.del_rider(newId, notify=False)
                        _log.debug(
                            'New ID %r exists, flag removal of duplicate',
                            newId)
                        delDest = True

                    # Check for restore of duplicate back to original
                    moveSrc = True  # replace src in events with dst
                    if not wasDupe:
                        # Is there another entry in the rdb with this id?
                        for idx, r in self.rdb.items():
                            chkId = r.get_id()
                            # unless entry is self
                            # Note: not wasDupe implies oldId == dbr.get_id()
                            if idx != oldId and chkId == oldId:
                                # Yes, restore backup, leave id in meet
                                # Note: No need to notify, events are closed
                                #       name will be updated on reload
                                moveSrc = False
                                restoreDbr = r
                                restoreIdx = idx  # index != id in this case
                                break

                    # Remove oldId from index
                    self.rdb.del_rider(oldId, notify=False)

                    # Add modified rider back into index
                    self.rdb.add_rider(dbr, notify=False, overwrite=False)

                    # Restore duplicate if oldId was freed up
                    if restoreDbr is not None:
                        _log.debug('Restore backup %s %s %r',
                                   restoreDbr.get_label(),
                                   restoreDbr.get_bibstr(), restoreIdx)
                        self.rdb.del_rider(restoreIdx, notify=False)
                        self.rdb.add_rider(restoreDbr,
                                           notify=False,
                                           overwrite=False)

                    # Convert backup rider into a new duplicate entry
                    if backupDbr is not None:
                        _log.debug('Save copy of duplicate rider: %s',
                                   backupDbr.get_id())
                        self.rdb.add_rider(backupDbr,
                                           notify=False,
                                           overwrite=False)

                    # Handle changes in event
                    oldSeries = res['rdb']['series'][1]
                    newSeries = res['rdb']['series'][2]
                    oldNo = res['rdb']['no'][1]
                    newNo = res['rdb']['no'][2]

                    if oldSeries == 'cat' or newSeries == 'cat':
                        if oldSeries != 'cat' and moveSrc:
                            if self.curevent is not None:
                                self.curevent.delrider(oldNo, oldSeries)
                        elif newSeries != 'cat' and moveSrc:
                            if self.curevent is not None:
                                self.curevent.delcat(oldNo, reload=False)
                                doreopen = True
                        else:
                            self.rdb.update_cats(oldNo, newNo, notify=False)
                            if self.curevent is not None:
                                self.curevent.changecat(oldNo,
                                                        newNo,
                                                        reload=False)
                                doreopen = True
                    else:
                        if self.curevent is not None:
                            if delDest:
                                self.curevent.delrider(newNo, newSeries)
                            if moveSrc:
                                _log.warning(
                                    '%s %s added to event, check result',
                                    dbr.get_label(), dbr.get_bibstr())
                                self.curevent.delrider(oldNo, oldSeries)
                                self.curevent.addrider(newNo, newSeries)
                            else:
                                self.curevent.addrider(newNo, newSeries)
                            doreopen = True

                    # Notify without idling
                    self.ridercb(None)

                    # then try to select the modified row
                    GLib.idle_add(self.select_rider,
                                  newId,
                                  priority=GLib.PRIORITY_LOW)

                    # reopen curevent if flagged after notify
                    if doreopen:
                        GLib.idle_add(self.event_reload)
                else:
                    for k in res['rdb']:
                        if res['rdb'][k][0]:
                            # notify via meet since id may be a duplicate
                            self._rcb(oldId)
                            break

    def rider_lookup_cb(self, menuitem, data=None):
        _log.info('Rider lookup not yet enabled')

    def rider_add_event_cb(self, menuitem, data=None):
        """Add currently selected entry to event"""
        if self._cur_rider_sel is not None and self._cur_rider_sel in self.rdb:
            if self.curevent is not None:
                selId = self._cur_rider_sel
                dbr = self.rdb[selId]
                series = dbr['series'].lower()
                if series == 'cat':
                    cat = dbr['no'].upper()
                    self.curevent.addcat(cat, reload=True)
                else:
                    self.curevent.addrider(dbr['no'], series)

    def rider_del_event_cb(self, menuitem, data=None):
        """Delete currently selected entry from event"""
        if self._cur_rider_sel is not None and self._cur_rider_sel in self.rdb:
            if self.curevent is not None:
                selId = self._cur_rider_sel
                dbr = self.rdb[selId]
                series = dbr['series'].lower()
                if series == 'cat':
                    cat = dbr['no'].upper()
                    self.curevent.delcat(cat, reload=True)
                else:
                    self.curevent.delrider(dbr['no'], series)

    def rider_delete_cb(self, menuitem, data=None):
        """Delete currently selected entry from riderdb"""
        if self._cur_rider_sel is not None and self._cur_rider_sel in self.rdb:
            doreopen = False
            selId = self._cur_rider_sel
            dbr = self.rdb[selId]
            series = dbr['series'].lower()
            wasDupe = False
            summary = dbr.summary()
            if selId != dbr.get_id():
                _log.debug('Removing duplicate %r stored as %r', dbr.get_id(),
                           selId)
                summary = 'Duplicate ' + summary
                wasDupe = True
            delId = dbr.get_id()
            riderNo = dbr['no']
            if uiutil.questiondlg(window=self.window,
                                  question='Delete %s from meet?' %
                                  (summary, ),
                                  title='Delete from Riderdb'):
                self._cur_rider_sel = None
                if wasDupe:
                    # Remove selection
                    self.rdb.del_rider(selId, notify=False)
                    _log.info('Duplicate %s %s removed', dbr.get_label(),
                              dbr.resname_bib())
                else:
                    # Is there another entry in the rdb with this id?
                    for idx, r in self.rdb.items():
                        chkId = r.get_id()
                        # unless entry is self
                        if idx != selId and chkId == selId:
                            # Yes, restore backup duplicate, leave id in meet
                            # Note: No need to notify since events are closed
                            #       name will be updated on reload
                            self.rdb.del_rider(selId, notify=False)
                            self.rdb.del_rider(idx, notify=False)
                            self.rdb.add_rider(r, notify=False)
                            GLib.idle_add(self.select_rider,
                                          chkId,
                                          priority=GLib.PRIORITY_LOW)
                            _log.info('Restored duplicate %s %s',
                                      r.get_label(), r.resname_bib())
                            break
                    else:
                        # Remove rider id from event
                        if self.curevent is not None:
                            if series == 'cat':
                                cat = dbr['no'].upper()
                                self.curevent.delcat(cat, reload=False)
                                doreopen = True
                            else:
                                self.curevent.delrider(dbr['no'], series)
                                _log.debug('Removed %s %s from event',
                                           dbr.get_label(), dbr.resname_bib())

                        # Remove entry from index
                        self.rdb.del_rider(selId, notify=False)
                        _log.info('Removed %s %s from meet', dbr.get_label(),
                                  dbr.resname_bib())
                self.ridercb(None)

                # reopen curevent if flagged after notify
                if doreopen:
                    GLib.idle_add(self.event_reload)
            else:
                _log.debug('Delete aborted')

    def get_colourmap(self):
        """Return a bg colourmap for the current display style."""
        if self._is_darkmode():
            return _COLOURMAP['dark']
        else:
            return _COLOURMAP['light']

    def _is_darkmode(self):
        """Return True if app appears to be running in dark mode."""
        ret = False
        with suppress(Exception):
            # estimate brightness of log view foreground text ignoring alpha
            fg = self.log_view.get_style_context().get_color(
                Gtk.StateFlags.NORMAL)
            bval = 0.3 * fg.red + 0.6 * fg.green + 0.1 * fg.blue
            _log.debug('Log view fg ~= %0.2f', bval)
            ret = bval > 0.5
        return ret

    def __init__(self, etype=None, lockfile=None):
        """Meet constructor."""
        self.loghandler = None  # set in loadconfig to meet dir
        self.exportpath = EXPORTPATH
        if etype not in ROADRACE_TYPES:
            etype = 'road'
        self.etype = etype
        self.meetlock = lockfile
        self.shortname = None
        self.title = ''
        self.host = ''
        self.subtitle = ''
        self.document = ''
        self.date = ''
        self.organiser = ''
        self.pcp = ''
        self.distance = None
        self.minavg = 20.0
        self.maxavg = 60.0
        self.diststr = ''
        self.linkbase = '.'
        self.provisionalstart = False
        self.indexlink = None
        self.nextlink = None
        self.prevlink = None

        self.remoteenable = False
        self.lifexport = False
        self.resfiles = True
        self.resarrival = False
        self.resdetail = False
        self.doprint = 'preview'
        self.announceresult = True

        # export locking flags
        self._export_lock = threading.Lock()
        self._export_thread = None

        # printer preferences
        paper = Gtk.PaperSize.new_custom('metarace-full', 'A4 for reports',
                                         595, 842, Gtk.Unit.POINTS)
        self.printprefs = Gtk.PrintSettings.new()
        self.pageset = Gtk.PageSetup.new()
        self.pageset.set_orientation(Gtk.PageOrientation.PORTRAIT)
        self.pageset.set_paper_size(paper)
        self.pageset.set_top_margin(0, Gtk.Unit.POINTS)
        self.pageset.set_bottom_margin(0, Gtk.Unit.POINTS)
        self.pageset.set_left_margin(0, Gtk.Unit.POINTS)
        self.pageset.set_right_margin(0, Gtk.Unit.POINTS)

        # hardware connections
        self.timertopic = None  # remote timer topic
        self._timer = decoder()
        self.timer = ''
        self._timer.setcb(self._timercb)
        self.timercb = None  # set by event app
        self._alttimer = timy()  # alttimer is always timy
        self.alttimer = ''
        self._alttimer.setcb(self._alttimercb)
        self.alttimercb = None  # set by event app
        self.announce = telegraph()
        self.announce.setcb(self._controlcb)
        self.anntopic = None
        self.mirrorpath = ''
        self.mirrorcmd = None
        self.mirrorfile = ''
        self.eventcode = ''

        b = uiutil.builder('roadmeet.ui')
        self.window = b.get_object('meet')
        self.window.connect('key-press-event', self.key_event)
        self.rfustat = uiutil.statButton()
        self.rfustat.set_sensitive(True)
        b.get_object('menu_clock').add(self.rfustat)
        self.rfustat.update('idle', '--')
        self.rfuact = False
        self.rfufail = 0
        self.status = b.get_object('status')
        self.log_buffer = b.get_object('log_buffer')
        self.log_view = b.get_object('log_view')
        #self.log_view.modify_font(uiutil.LOGVIEWFONT)
        self.log_scroll = b.get_object('log_box').get_vadjustment()
        self.decoder_configure = b.get_object('menu_timing_configure')
        self.event_box = b.get_object('event_box')
        self.stat_but = uiutil.statButton()
        b.get_object('event_stat_but').add(self.stat_but)
        self.action_model = b.get_object('event_action_model')
        self.action_combo = b.get_object('event_action_combo')
        self.action_entry = b.get_object('event_action_entry')
        b.get_object('event_stat_hbox').set_focus_chain(
            [self.action_combo, self.action_entry, self.action_combo])
        self.notebook = b.get_object('meet_nb')

        # prepare local scratch pad ? can these be removed?
        self.an_cur_lap = tod.ZERO
        self.an_cur_split = tod.ZERO
        self.an_cur_bunchid = 0
        self.an_cur_bunchcnt = 0
        self.an_last_time = None
        self.an_cur_start = tod.ZERO

        # setup context menu handles
        self._rider_menu = b.get_object('rider_context')
        self._rider_menu_edit = b.get_object('rider_edit')
        self._rider_menu_lookup = b.get_object('rider_lookup')
        self._rider_menu_del = b.get_object('rider_del')
        self._rider_menu_delevt = b.get_object('rider_delevt')
        self._rider_menu_addevt = b.get_object('rider_addevt')
        self._cur_rider_sel = None
        self._cur_model = None

        b.connect_signals(self)

        # run state
        self.running = True
        self.started = False
        self.curevent = None

        # connect UI log handlers
        _log.debug('Connecting interface log handlers')
        rootlogger = logging.getLogger()
        f = logging.Formatter(metarace.LOGFORMAT)
        self.statusHandler = uiutil.statusHandler(self.status)
        self.statusHandler.setFormatter(f)
        self.statusHandler.setLevel(logging.INFO)  # show info+
        rootlogger.addHandler(self.statusHandler)
        self.logHandler = uiutil.textViewHandler(self.log_buffer,
                                                 self.log_view,
                                                 self.log_scroll)
        self.logHandler.setFormatter(f)
        self.logHandler.setLevel(logging.INFO)  # show info+
        rootlogger.addHandler(self.logHandler)

        # Build a rider list store and view
        self._rlm = Gtk.ListStore(
            str,  # BIB.series 0
            int,  # text style 1
            str,  # name 2 
            str,  # rsvd
            str,  # categories 4
            str,  # Refid 5
            str,  # tooltip 6
            object,  # rider ref 7
        )
        t = Gtk.TreeView(self._rlm)
        t.set_reorderable(True)
        t.set_rules_hint(True)
        t.set_tooltip_column(6)
        uiutil.mkviewcoltxt(t, 'No.', 0, calign=1.0, style=1)
        uiutil.mkviewcoltxt(t,
                            'Rider',
                            2,
                            expand=True,
                            cb=self._editname_cb,
                            style=1)
        #uiutil.mkviewcoltxt(t, 'Org', 3, cb=self._editcol_cb)
        uiutil.mkviewcoltxt(t, 'Cats', 4, width=80, cb=self._editcol_cb)
        uiutil.mkviewcoltxt(t, 'Refid', 5, width=80, cb=self._editcol_cb)
        t.show()
        t.connect('button_press_event', self._view_button_press)
        self._rlv = t
        b.get_object('riders_box').add(t)

        # Build a cat list store and view
        self._clm = Gtk.ListStore(
            str,  # ID 0
            str,  # Title 1
            str,  # Subtitle 2
            str,  # Footer 3
            str,  # Target Laps 4
            str,  # Distance 5
            str,  # Start Offset 6
            object,  # Rider ref 7
            int,  # Text style 8
        )
        t = Gtk.TreeView(self._clm)
        t.set_reorderable(True)
        t.set_rules_hint(True)
        uiutil.mkviewcoltxt(t, 'ID', 0, calign=0.0, width=40, style=8)
        uiutil.mkviewcoltxt(t,
                            'Title',
                            1,
                            width=140,
                            cb=self._catcol_cb,
                            style=8)
        uiutil.mkviewcoltxt(t,
                            'Subtitle',
                            2,
                            expand=True,
                            cb=self._catcol_cb,
                            style=8)
        uiutil.mkviewcoltxt(t,
                            'Footer',
                            3,
                            width=140,
                            maxwidth=140,
                            cb=self._catcol_cb,
                            style=8)
        uiutil.mkviewcoltxt(t,
                            'Laps',
                            4,
                            width=40,
                            calign=1.0,
                            cb=self._catcol_cb)
        uiutil.mkviewcoltxt(t,
                            'Distance',
                            5,
                            width=40,
                            calign=1.0,
                            cb=self._catcol_cb)
        uiutil.mkviewcoltxt(t,
                            'Start Offset',
                            6,
                            width=50,
                            calign=1.0,
                            cb=self._catcol_cb)

        t.show()
        t.connect('button_press_event', self._view_button_press)
        self._clv = t
        b.get_object('cat_box').add(t)

        # get rider db
        _log.debug('Add riderdb')
        self.rdb = riderdb.riderdb()
        self.rdb.set_notify(self._rcb)
        self._tagmap = {}
        self._maptag = {}

        # select event page in notebook.
        self.notebook.set_current_page(0)

        # start timer
        GLib.timeout_add_seconds(1, self.timeout)


class fakemeet(roadmeet):
    """Non-interactive meet wrapper"""

    def __init__(self, rdb):
        self.etype = 'road'
        self.rdb = rdb
        self._timer = decoder()
        self._alttimer = timy()
        self.stat_but = uiutil.statButton()
        self.action_model = Gtk.ListStore(str, str)
        self.action_model.append(['a', 'a'])
        self.action_combo = Gtk.ComboBox()
        self.action_combo.set_model(self.action_model)
        self.action_combo.set_active(0)
        self.log_view = None
        self.announce = telegraph()
        self.title = ''
        self.host = ''
        self.subtitle = ''
        self.date = ''
        self.document = ''
        self.organiser = ''
        self.pcp = ''
        self.distance = None
        self.diststr = ''
        self.linkbase = '.'
        self.provisionalstart = False
        self.indexlink = None
        self.nextlink = None
        self.prevlink = None
        self.eventcode = ''
        self.shortname = ''
        self.mirrorfile = ''

    def cmd_announce(self, command, msg):
        return False

    def rider_announce(self, rvec):
        return False

    def timer_announce(self, evt, timer=None, source=''):
        return False

    def loadconfig(self):
        """Load meet config from disk."""
        cr = jsonconfig.config()
        cr.add_section('roadmeet', _CONFIG_SCHEMA)
        cr.merge(metarace.sysconf, 'roadmeet')
        cr.load(CONFIGFILE)
        cr.export_section('roadmeet', self)


def edit_defaults():
    """Run a sysconf editor dialog"""
    metarace.sysconf.add_section('roadmeet', _CONFIG_SCHEMA)
    metarace.sysconf.add_section('rms', _RMS_SCHEMA)
    metarace.sysconf.add_section('irtt', _IRTT_SCHEMA)
    metarace.sysconf.add_section('trtt', _TRTT_SCHEMA)
    metarace.sysconf.add_section('export', _EXPORT_SCHEMA)
    metarace.sysconf.add_section('telegraph', _TG_SCHEMA)
    metarace.sysconf.add_section('thbc', _THBC_SCHEMA)
    metarace.sysconf.add_section('rru', _RRU_SCHEMA)
    metarace.sysconf.add_section('rrs', _RRS_SCHEMA)
    metarace.sysconf.add_section('timy', _TIMY_SCHEMA)
    metarace.sysconf.add_section('drelay', _DRELAY_SCHEMA)
    cfgres = uiutil.options_dlg(title='Edit Default Configuration',
                                sections={
                                    'roadmeet': {
                                        'title': 'Meet',
                                        'schema': _CONFIG_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'rms': {
                                        'title': 'Road/Cross',
                                        'schema': _RMS_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'irtt': {
                                        'title': 'Individual TT',
                                        'schema': _IRTT_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'trtt': {
                                        'title': 'Teams TT',
                                        'schema': _TRTT_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'export': {
                                        'title': 'Export',
                                        'schema': _EXPORT_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'telegraph': {
                                        'title': 'Telegraph',
                                        'schema': _TG_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'timy': {
                                        'title': 'Timy',
                                        'schema': _TIMY_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'thbc': {
                                        'title': 'THBC',
                                        'schema': _THBC_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'rru': {
                                        'title': 'RR USB',
                                        'schema': _RRU_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'rrs': {
                                        'title': 'RR System',
                                        'schema': _RRS_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                    'drelay': {
                                        'title': 'D-Relay',
                                        'schema': _DRELAY_SCHEMA,
                                        'object': metarace.sysconf,
                                    },
                                })

    # check for sysconf changes:
    syschange = False
    for sec in cfgres:
        for key in cfgres[sec]:
            if cfgres[sec][key][0]:
                syschange = True
                break
    if syschange:
        backup = metarace.SYSCONF + '.bak'
        _log.info('Backing up old defaults to %r', backup)
        try:
            if os.path.exists(backup):
                os.unlink(backup)
            os.link(metarace.SYSCONF, backup)
        except Exception as e:
            _log.warning('%s saving defaults backup: %s', e.__class__.__name__,
                         e)
        _log.info('Edit default: Saving sysconf to %r', metarace.SYSCONF)
        with metarace.savefile(metarace.SYSCONF, perm=0o600) as f:
            metarace.sysconf.write(f)
    else:
        _log.info('Edit default: No changes to save')
    return 0


def loadmeet():
    """Select meet folder with chooser dialog"""
    return uiutil.chooseFolder(title='Open Meet Folder',
                               path=metarace.DATA_PATH)


def createmeet():
    """Create a new empty meet folder"""
    ret = None
    count = 0
    dname = 'road_' + tod.datetime.now().date().isoformat()
    cname = dname
    while count < 100:
        mpath = os.path.join(metarace.DATA_PATH, cname)
        if not os.path.exists(mpath):
            os.makedirs(mpath)
            _log.info('Created empty meet folder: %r', mpath)
            ret = mpath
            break
        count += 1
        cname = dname + '_%02d' % (count)
    if ret is None:
        _log.error('Unable to create empty meet folder')
    return ret


def main():
    """Run the road meet application as a console script."""
    chk = Gtk.init_check()
    if not chk[0]:
        print('Unable to init Gtk display')
        sys.exit(-1)

    # attach a console log handler to the root logger
    ch = logging.StreamHandler()
    ch.setLevel(metarace.LOGLEVEL)
    fh = logging.Formatter(metarace.LOGFORMAT)
    ch.setFormatter(fh)
    logging.getLogger().addHandler(ch)

    try:
        GLib.set_prgname(PRGNAME)
        GLib.set_application_name(APPNAME)
        Gtk.Window.set_default_icon_name(metarace.ICON)
        mset = Gtk.Settings.get_default()
        mset.set_property('gtk-menu-bar-accel', 'F24')
    except Exception as e:
        _log.debug('%s setting property: %s', e.__class__.__name__, e)

    doconfig = False
    configpath = None
    if len(sys.argv) > 2:
        _log.error('Usage: roadmeet [PATH]')
        sys.exit(1)
    elif len(sys.argv) == 2:
        if sys.argv[1] == '--edit-default':
            doconfig = True
            configpath = metarace.DEFAULTS_PATH
            _log.debug('Edit defaults, configpath: %r', configpath)
        elif sys.argv[1] == '--create':
            configpath = createmeet()
        else:
            configpath = sys.argv[1]
    else:
        configpath = loadmeet()
    configpath = metarace.config_path(configpath)
    if configpath is None:
        _log.debug('Missing path, command: %r', sys.argv)
        _log.error('Error opening meet')
        if not os.isatty(sys.stdout.fileno()):
            uiutil.messagedlg(
                message='Error opening meet.',
                title='Roadmeet: Error',
                subtext='Roadmeet was unable to open a meet folder.')
        sys.exit(-1)

    lf = metarace.lockpath(configpath)
    if lf is None:
        _log.error('Unable to lock meet config, already in use')
        if not os.isatty(sys.stdout.fileno()):
            uiutil.messagedlg(
                message='Meet folder is locked.',
                title='Roadmeet: Locked',
                subtext=
                'Another application has locked the meet folder for use.')
        sys.exit(-1)
    _log.debug('Entering meet folder %r', configpath)
    os.chdir(configpath)
    metarace.init()
    if doconfig:
        return edit_defaults()
    else:
        app = roadmeet(None, lf)
        mp = configpath
        if mp.startswith(metarace.DATA_PATH):
            mp = mp.replace(metarace.DATA_PATH + '/', '')
        app.statusHandler.set_basemsg('Meet Folder: ' + mp)
        app.loadconfig()
        app.window.show()
        app.start()
        return Gtk.main()


if __name__ == '__main__':
    sys.exit(main())
