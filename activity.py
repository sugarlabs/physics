# Physics, a 2D Physics Playground for Kids

# Copyright (C) 2008 Alex Levenson and Brian Jordan
# Copyright (C) 2012 Daniel Francis
# Copyright (C) 2012-14  Walter Bender
# Copyright (C) 2013 Sai Vineet
# Copyright (C) 2013-14 Ignacio Rodriguez
# Copyright (C) 2012-13 Sugar Labs

#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import csv
import tempfile
import json
import logging
from gettext import gettext as _

import pygame
import sugargame
import sugargame.canvas

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from sugar3.activity import activity
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.alert import ConfirmationAlert
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.style import GRID_CELL_SIZE
from sugar3.datastore import datastore
from sugar3.graphics.objectchooser import get_preview_pixbuf

import tools
import physics


class PhysicsActivity(activity.Activity):
    def __init__(self, handle):
        super(PhysicsActivity, self).__init__(handle)
        self.metadata['mime_type'] = 'application/x-physics-activity'
        self.add_events(Gdk.EventMask.ALL_EVENTS_MASK |
                        Gdk.EventMask.VISIBILITY_NOTIFY_MASK)

        self.connect('visibility-notify-event', self._focus_event)
        self.connect('window-state-event', self._window_event)

        self._canvas = sugargame.canvas.PygameCanvas(self)
        self.game = physics.main(self)
        self.preview = None
        self.build_toolbar()

        self.set_canvas(self._canvas)
        Gdk.Screen.get_default().connect('size-changed',
                                         self.__configure_cb)

        logging.debug(os.path.join(
                      activity.get_activity_root(), 'data', 'data'))
        self._canvas.run_pygame(self.game.run)

    def __configure_cb(self, event):
        ''' Screen size has changed '''
        self.write_file(os.path.join(
                        activity.get_activity_root(), 'data', 'data'))
        pygame.display.set_mode((Gdk.Screen.width(),
                                 Gdk.Screen.height() - 2 * GRID_CELL_SIZE),
                                pygame.RESIZABLE)
        self.read_file(os.path.join(
                       activity.get_activity_root(), 'data', 'data'))
        self.game.run(True)

    def read_file(self, file_path):
        self.game.read_file(file_path)

    def write_file(self, file_path):
        self.game.write_file(file_path)

    def get_preview(self):
        ''' Custom preview code to get image from pygame. '''
        return self._canvas.get_preview()

        def save_func(buf, data):
            data.append(buf)

        pixbuf.save_to_callback(save_func, 'png', user_data=preview_data)
        preview_data = ''.join(preview_data)

        return preview_data

    def build_toolbar(self):
        self.max_participants = 1
        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        create_toolbar = ToolbarButton()
        create_toolbar.props.page = Gtk.Toolbar()
        create_toolbar.props.icon_name = 'magicpen'
        create_toolbar.props.label = _('Create')
        toolbar_box.toolbar.insert(create_toolbar, -1)
        self._insert_create_tools(create_toolbar)

        self._insert_stop_play_button(toolbar_box.toolbar)

        separator = Gtk.SeparatorToolItem()
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        clear_trace = ToolButton('clear-trace')
        clear_trace.set_tooltip(_('Clear Trace Marks'))
        clear_trace.set_accelerator(_('<ctrl>x'))
        clear_trace.connect('clicked', self.clear_trace_cb)
        clear_trace.set_sensitive(False)
        toolbar_box.toolbar.insert(clear_trace, -1)
        clear_trace.show()
        self.clear_trace = clear_trace

        self._insert_clear_all_button(toolbar_box.toolbar)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop = StopButton(self)
        toolbar_box.toolbar.insert(stop, -1)
        stop.show()

        separator = Gtk.SeparatorToolItem()
        activity_button.props.page.insert(separator, -1)
        separator.show()

        export_json = ToolButton('save-as-json')
        export_json.set_tooltip(_('Export tracked objects to journal'))
        export_json.connect('clicked', self._export_json_cb)
        activity_button.props.page.insert(export_json, -1)
        export_json.show()

        export_csv = ToolButton('save-as-csv')
        export_csv.set_tooltip(_('Export tracked objects to journal'))
        export_csv.connect('clicked', self._export_csv_cb)
        activity_button.props.page.insert(export_csv, -1)
        export_csv.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show_all()
        create_toolbar.set_expanded(True)
        return toolbar_box

    def can_close(self):
        self.preview = self.get_preview()
        self.game.loop = False
        return True

    def _insert_stop_play_button(self, toolbar):
        self.stop_play_state = True
        self.stop_play = ToolButton('media-playback-stop')
        self.stop_play.set_tooltip(_('Stop'))
        self.stop_play.set_accelerator(_('<ctrl>space'))
        self.stop_play.connect('clicked', self.stop_play_cb)
        toolbar.insert(self.stop_play, -1)
        self.stop_play.show()

    def _insert_clear_all_button(self, toolbar):
        self.clear_all = ToolButton('clear_all')
        self.clear_all.set_tooltip(_('Erase All'))
        self.clear_all.set_accelerator(_('<ctrl>a'))
        self.clear_all.connect('clicked', self.clear_all_cb)
        toolbar.insert(self.clear_all, -1)
        self.clear_all.set_sensitive(False)
        self.clear_all.show()

    def _insert_create_tools(self, create_toolbar):

        def _insert_item(toolbar, item, pos=-1):
            if hasattr(toolbar, 'insert'):
                toolbar.insert(item, pos)
            else:
                toolbar.props.page.insert(item, pos)

        # Make + add the component buttons
        self.radioList = {}
        firstButton = None
        for i, c in enumerate(tools.allTools):
            if i == 0:
                button = RadioToolButton(group=None)
                firstbutton = button
            else:
                button = RadioToolButton(group=firstbutton)
            button.set_icon_name(c.icon)
            button.set_tooltip(c.toolTip)
            button.set_accelerator(c.toolAccelerator)
            button.connect('clicked', self.radioClicked)
            palette = self._build_palette(c)
            if palette is not None:
                button.get_palette().set_content(palette)
            _insert_item(create_toolbar, button, -1)
            button.show()
            self.radioList[button] = c.name

    def __icon_path(self, name):
        activity_path = activity.get_bundle_path()
        icon_path = os.path.join(activity_path, 'icons',
                                 name+".svg")
        return icon_path

    def _build_palette(self, tool):
        if tool.palette_enabled:
            if tool.palette_mode == tools.PALETTE_MODE_ICONS:
                vbox = Gtk.VBox()
                for settings in tool.palette_settings:
                    hbox = Gtk.HBox()
                    firstButton = None
                    for i in range(0, settings['icon_count']):
                        if i == 0:
                            button = RadioToolButton(group=None)
                            firstbutton = button
                        else:
                            button = RadioToolButton(group=firstbutton)
                        button.set_icon_name(settings['icons'][i])
                        button.connect('clicked',
                                       self._palette_icon_clicked,
                                       tool.name, 
                                       settings['name'],
                                       settings['icon_values'][i])
                        if settings['active'] == settings['icons'][i]:
                            button.set_active(True)
                        hbox.pack_start(button, False, False, 0)
                    vbox.add(hbox)
                vbox.show_all()
                return vbox

        return None

    def _palette_icon_clicked(self, button, toolname, value_name, value):
        for tool in tools.allTools:
            if tool.name == toolname:
                if hasattr(tool, 'palette_data_type'):
                    tool.palette_data_type = value
                else:
                    tool.palette_data[value_name] = value

    def clear_trace_alert_cb(self, alert, response):
        self.remove_alert(alert)
        if response is Gtk.ResponseType.OK:
            self.game.full_pos_list = [[] for _ in self.game.full_pos_list]
            self.game.tracked_bodies = 0

    def clear_trace_cb(self, button):
        clear_trace_alert = ConfirmationAlert()
        clear_trace_alert.props.title = _('Are You Sure?')
        clear_trace_alert.props.msg = \
            _('All trace points will be erased. This cannot be undone!')
        clear_trace_alert.connect('response', self.clear_trace_alert_cb)
        self.add_alert(clear_trace_alert)

    def stop_play_cb(self, button):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                             action='stop_start_toggle'))
        self.stop_play_state = not self.stop_play_state

        if self.stop_play_state:
            self.stop_play.set_icon('media-playback-stop')
            self.stop_play.set_tooltip(_('Stop'))
        else:
            self.stop_play.set_icon('media-playback-start')
            self.stop_play.set_tooltip(_('Start'))

    def clear_all_cb(self, button):
        def clear_all_alert_cb(alert, response_id):
            self.remove_alert(alert)
            if response_id is Gtk.ResponseType.OK:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                     action='clear_all'))
        if len(self.game.world.world.GetBodyList()) > 2:
            print len(self.game.world.world.GetBodyList())
            clear_all_alert = ConfirmationAlert()
            clear_all_alert.props.title = _('Are You Sure?')
            clear_all_alert.props.msg = \
                _('All your work will be discarded. This cannot be undone!')
            clear_all_alert.connect('response', clear_all_alert_cb)
            self.add_alert(clear_all_alert)

    def radioClicked(self, button):
        pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                             action=self.radioList[button]))

    def _focus_event(self, event, data=None):
        ''' Send focus events to pygame to allow it to idle when in
        background. '''
        if not self.game.pygame_started:
            logging.debug('focus_event: pygame not yet initialized')
            return
        if data.state == Gdk.VisibilityState.FULLY_OBSCURED:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                 action='focus_out'))
        else:
            self.game.show_fake_cursor = True
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                 action='focus_in'))

    def _export_json_cb(self, button):
        jobject = datastore.create()
        jobject.metadata['title'] = _('Physics export')
        jobject.metadata['mime_type'] = 'text/plain'

        tmp_dir = os.path.join(self.get_activity_root(), 'instance')
        fd, file_path = tempfile.mkstemp(dir=tmp_dir)
        os.close(fd)

        data = self.game.full_pos_list
        jsonfile = open(file_path, 'wb')
        jsonfile.write(json.dumps(data))
        jsonfile.close()

        jobject.set_file_path(os.path.abspath(jsonfile.name))
        datastore.write(jobject)

    def _export_csv_cb(self, button):
        jobject = datastore.create()
        jobject.metadata['title'] = _('Physics export')
        jobject.metadata['mime_type'] = 'text/csv'

        tmp_dir = os.path.join(self.get_activity_root(), 'instance')
        fd, file_path = tempfile.mkstemp(dir=tmp_dir)
        os.close(fd)

        data = self.game.full_pos_list
        csvfile = open(file_path, 'wb')
        writer = csv.writer(csvfile)
        writer.writerows(data)
        csvfile.close()

        jobject.set_file_path(os.path.abspath(csvfile.name))
        datastore.write(jobject)

    def _window_event(self, window, event):
        ''' Send focus out event to pygame when switching to a desktop
        view. '''
        if event.changed_mask & Gdk.WindowState.ICONIFIED:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                 action='focus_out'))
