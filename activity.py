# Physics, a 2D Physics Playground for Kids

# Copyright (C) 2008  Alex Levenson and Brian Jordan
# Copyright (C) 2012  Daniel Francis
# Copyright (C) 2012-13  Walter Bender
# Copyright (C) 2013  Sai Vineet
# Copyright (C) 2012-13  Sugar Labs

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
import gtk
import csv
import tempfile
import json
from gettext import gettext as _
import logging

import pygame
import sugargame
import sugargame.canvas

from sugar.activity import activity
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.alert import ConfirmationAlert
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbarbox import ToolbarButton
from sugar.graphics.style import GRID_CELL_SIZE
from sugar.datastore import datastore
from sugar.graphics.icon import Icon
from sugar.graphics import style

import tools
import physics


class PhysicsActivity(activity.Activity):
    def __init__(self, handle):
        super(PhysicsActivity, self).__init__(handle)
        self.metadata['mime_type'] = 'application/x-physics-activity'
        self.add_events(gtk.gdk.ALL_EVENTS_MASK |
                        gtk.gdk.VISIBILITY_NOTIFY_MASK)

        self.connect('visibility-notify-event', self._focus_event)
        self.connect('window-state-event', self._window_event)

        self._canvas = sugargame.canvas.PygameCanvas(self)
        self.game = physics.main(self)
        self.preview = None
        self.build_toolbar()

        self.set_canvas(self._canvas)
        gtk.gdk.screen_get_default().connect('size-changed',
                                             self.__configure_cb)

        logging.debug(os.path.join(
                      activity.get_activity_root(), 'data', 'data'))
        self._canvas.run_pygame(self.game.run)

    def __configure_cb(self, event):
        ''' Screen size has changed '''
        self.write_file(os.path.join(
                        activity.get_activity_root(), 'data', 'data'))
        pygame.display.set_mode((gtk.gdk.screen_width(),
                                 gtk.gdk.screen_height() - 2 * GRID_CELL_SIZE),
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
        if self.preview:
            return self.preview
        surface = pygame.display.get_surface()
        width, height = surface.get_width(), surface.get_height()
        pixbuf = gtk.gdk.pixbuf_new_from_data(pygame.image.tostring(surface,
                                                                    'RGB'),
                                              gtk.gdk.COLORSPACE_RGB, 0, 8,
                                              width, height,
                                              3 * width)
        pixbuf = pixbuf.scale_simple(300, 225, gtk.gdk.INTERP_BILINEAR)

        preview_data = []

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
        create_toolbar.props.page = gtk.Toolbar()
        create_toolbar.props.icon_name = 'magicpen'
        create_toolbar.props.label = _('Create')
        toolbar_box.toolbar.insert(create_toolbar, -1)
        self._insert_create_tools(create_toolbar)

        self._insert_stop_play_button(toolbar_box.toolbar)

        separator = gtk.SeparatorToolItem()
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

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_size_request(0, -1)
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop = StopButton(self)
        toolbar_box.toolbar.insert(stop, -1)
        stop.show()

        separator = gtk.SeparatorToolItem()
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
        for c in tools.allTools:
            button = RadioToolButton(named_icon=c.icon)
            if firstButton:
                button.set_group(firstButton)
            else:
                button.set_group(None)
                firstButton = button

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
            if tool.palette_mode == tools.PALETTE_MODE_SLIDER_ICON:
                settings = tool.palette_settings
                hbox = gtk.HBox()
                hbox.set_size_request(-1, 50)

                icon1 = Icon()
                icon1.set_file(self.__icon_path(settings['icon1']))
                icon2 = Icon()
                icon2.set_file(self.__icon_path(settings['icon2']))

                adj = gtk.Adjustment(lower=settings['min'],
                                     upper=settings['max'],
                                     step_incr=1)
                slider = gtk.HScale(adjustment=adj)
                slider.set_size_request(200, 25)
                slider.connect("value-changed", self._slider_palette,
                               tool.name)
                slider.set_value(settings['min'])

                hbox.pack_start(icon1, False, False, 0)
                hbox.pack_start(slider, True, True, 0)
                hbox.pack_start(icon2, False, False, 0)
                hbox.show_all()
                return hbox
            elif tool.palette_mode == tools.PALETTE_MODE_SLIDER_LABEL:
                table = gtk.Table(rows=len(tool.palette_settings), columns=2)

                table.set_row_spacings(spacing=style.DEFAULT_SPACING)
                table.set_col_spacings(spacing=style.DEFAULT_SPACING)
                for row, settings in enumerate(tool.palette_settings):
                    label = gtk.Label(settings["label"])

                    adj = gtk.Adjustment(lower=settings['min'],
                                         upper=settings['max'],
                                         step_incr=1)
                    slider = gtk.HScale(adjustment=adj)

                    slider.set_size_request(200, 50)
                    slider.connect("value-changed", self._slider_label_palette,
                                   tool.name, settings['data'])
                    slider.set_value(settings['min'])

                    table.attach(label,
                                 left_attach=0,
                                 right_attach=1,
                                 top_attach=row,
                                 bottom_attach=row+1)
                    table.attach(slider,
                                 left_attach=1,
                                 right_attach=2,
                                 top_attach=row,
                                 bottom_attach=row+1)
                table.show_all()
                return table
            elif tool.palette_mode == tools.PALETTE_MODE_ICONS:
                vbox = gtk.VBox()
                for settings in tool.palette_settings:
                    hbox = gtk.HBox()
                    firstButton = None
                    for i in range(0, settings['icon_count']):
                        button = RadioToolButton(
                            named_icon=settings['icons'][i])
                        if firstButton:
                            button.set_group(firstButton)
                        else:
                            button.set_group(None)
                            firstButton = button
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
                tool.palette_data[value_name] = value

    def _slider_label_palette(self, slider, toolname, dataname):
        value = slider.get_value()
        for tool in tools.allTools:
            if tool.name == toolname:
                tool.palette_data[dataname] = value

    def _slider_palette(self, slider, toolname):
        value = slider.get_value()
        for tool in tools.allTools:
            if tool.name == toolname:
                tool.palette_data = value

    def clear_trace_alert_cb(self, alert, response):
        self.remove_alert(alert)
        if response is gtk.RESPONSE_OK:
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
            if response_id is gtk.RESPONSE_OK:
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
        if data.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
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
        if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                 action='focus_out'))
