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

from gi.repository import GObject
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
from sugar3.graphics.alert import Alert
from sugar3.graphics.icon import Icon
from sugar3.graphics.xocolor import XoColor
from sugar3 import profile

import telepathy
from dbus.service import signal
from dbus.gobject_service import ExportedGObject
from sugar3.presence import presenceservice
from sugar3.presence.tubeconn import TubeConnection

import tools
import physics

SERVICE = 'org.laptop.physics'
IFACE = SERVICE
PATH = '/org/laptop/physics'


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

        self._constructors = {}
        self.build_toolbar()

        self.set_canvas(self._canvas)
        Gdk.Screen.get_default().connect('size-changed',
                                         self.__configure_cb)

        logging.debug(os.path.join(
                      activity.get_activity_root(), 'data', 'data'))
        self._canvas.run_pygame(self.game.run)
        GObject.idle_add(self._setup_sharing)

    def _setup_sharing(self):
        self.we_are_sharing = False

        if self.shared_activity:
            # We're joining
            if not self.get_shared():
                xocolors = XoColor(profile.get_color().to_string())
                share_icon = Icon(icon_name='zoom-neighborhood',
                                  xo_color=xocolors)
                self._joined_alert = Alert()
                self._joined_alert.props.icon = share_icon
                self._joined_alert.props.title = _('Please wait')
                self._joined_alert.props.msg = _('Starting connection...')
                self.add_alert(self._joined_alert)
                self._waiting_cursor()

        self._setup_presence_service()

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
        self.max_participants = 4

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
                palette.show()
                button.get_palette().set_content(palette)
            _insert_item(create_toolbar, button, -1)
            button.show()
            self.radioList[button] = c.name
            if hasattr(c, 'constructor'):
                self._constructors[c.name] = \
                    self.game.toolList[c.name].constructor

    def __icon_path(self, name):
        activity_path = activity.get_bundle_path()
        icon_path = os.path.join(activity_path, 'icons',
                                 name+".svg")
        return icon_path

    def _build_palette(self, tool):
        if tool.palette_enabled:
            if tool.palette_mode == tools.PALETTE_MODE_ICONS:
                grid = Gtk.Grid()
                for s, settings in enumerate(tool.palette_settings):
                    self.game.toolList[tool.name].buttons.append([])
                    firstButton = None
                    for i, icon_value in enumerate(settings['icon_values']):
                        if i == 0:
                            button = RadioToolButton(group=None)
                            firstbutton = button
                        else:
                            button = RadioToolButton(group=firstbutton)
                        button.set_icon_name(settings['icons'][i])
                        button.connect('clicked',
                                       self._palette_icon_clicked,
                                       tool.name, 
                                       s,
                                       settings['name'],
                                       icon_value)
                        grid.attach(button, i, s, 1, 1)
                        self.game.toolList[tool.name].buttons[s].append(button)
                        button.show()
                        if settings['active'] == settings['icons'][i]:
                            button.set_icon_name(settings['icons'][i] + \
                                                 '-selected')
                            button.set_active(True)
                return grid
        else:
            return None

    def _palette_icon_clicked(self, widget, toolname, s, value_name, value):
        for tool in tools.allTools:
            if tool.name == toolname:
                # Radio buttons are not highlighting in the palette
                # so adding highlight by hand
                setting = self.game.toolList[tool.name].palette_settings[s]
                for i, button in enumerate(
                        self.game.toolList[tool.name].buttons[s]):
                    icon_name = setting['icons'][i]
                    if button == widget:
                        button.set_icon_name(icon_name + '-selected')
                    else:
                        button.set_icon_name(icon_name)
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
            self.stop_play.set_icon_name('media-playback-stop')
            self.stop_play.set_tooltip(_('Stop'))
        else:
            self.stop_play.set_icon_name('media-playback-start')
            self.stop_play.set_tooltip(_('Start'))

    def clear_all_cb(self, button):
        def clear_all_alert_cb(alert, response_id):
            self.remove_alert(alert)
            if response_id is Gtk.ResponseType.OK:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                     action='clear_all'))
        if len(self.game.world.world.GetBodyList()) > 2:
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

    def _setup_presence_service(self):
        ''' Setup the Presence Service. '''
        self.pservice = presenceservice.get_instance()

        owner = self.pservice.get_owner()
        self.owner = owner
        self.buddies = [owner]
        self._share = ''
        self.connect('shared', self._shared_cb)
        self.connect('joined', self._joined_cb)

    def _shared_cb(self, activity):
        ''' Either set up initial share...'''
        if self.get_shared_activity() is None:
            logging.error('Failed to share or join activity ... \
                shared_activity is null in _shared_cb()')
            return

        self.initiating = True
        self.waiting = False
        self.we_are_sharing = True
        logging.debug('I am sharing...')

        self.conn = self.shared_activity.telepathy_conn
        self.tubes_chan = self.shared_activity.telepathy_tubes_chan
        self.text_chan = self.shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(
            'NewTube', self._new_tube_cb)

        logging.debug('This is my activity: making a tube...')
        id = self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            SERVICE, {})

    def _joined_cb(self, activity):
        ''' ...or join an exisiting share. '''
        if self.get_shared_activity() is None:
            logging.error('Failed to share or join activity ... \
                shared_activity is null in _shared_cb()')
            return

        self.initiating = False
        logging.debug('I joined a shared activity.')

        self.conn = self.shared_activity.telepathy_conn
        self.tubes_chan = self.shared_activity.telepathy_tubes_chan
        self.text_chan = self.shared_activity.telepathy_text_chan

        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal(\
            'NewTube', self._new_tube_cb)

        logging.debug('I am joining an activity: waiting for a tube...')
        self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb,
            error_handler=self._list_tubes_error_cb)

        self.waiting = True

        if self._joined_alert is not None:
            self.remove_alert(self._joined_alert)
            self._joined_alert = None
            self._restore_cursor()
            self.we_are_sharing = True

    def _restore_cursor(self):
        ''' No longer waiting, so restore standard cursor. '''
        if not hasattr(self, 'get_window'):
            return
        self.get_window().set_cursor(self.old_cursor)

    def _waiting_cursor(self):
        ''' Waiting, so set watch cursor. '''
        if not hasattr(self, 'get_window'):
            return
        self.old_cursor = self.get_window().get_cursor()
        self.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))

    def _list_tubes_reply_cb(self, tubes):
        ''' Reply to a list request. '''
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        ''' Log errors. '''
        logging.error('ListTubes() failed: %s', e)

    def _new_tube_cb(self, id, initiator, type, service, params, state):
        ''' Create a new tube. '''
        logging.debug('New tube: ID=%d initator=%d type=%d service=%s '
                     'params=%r state=%d', id, initiator, type, service,
                     params, state)

        if (type == telepathy.TUBE_TYPE_DBUS and service == SERVICE):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self.tubes_chan[ \
                              telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

            tube_conn = TubeConnection(self.conn,
                self.tubes_chan[telepathy.CHANNEL_TYPE_TUBES], id, \
                group_iface=self.text_chan[telepathy.CHANNEL_INTERFACE_GROUP])

            self.chattube = ChatTube(tube_conn, self.initiating, \
                self.event_received_cb)

    def event_received_cb(self, text):
        ''' Data is passed as tuples: cmd:text '''
        dispatch_table = {'C': self._construct_shared_circle,
                          'B': self._construct_shared_box,
                          'T': self._construct_shared_triangle,
                          'P': self._construct_shared_polygon,
                          'M': self._construct_shared_magicpen,
                          'j': self._add_shared_joint,
                          'p': self._add_shared_pin,
                          'm': self._add_shared_motor,
                          't': self._add_shared_track,
                          'c': self._add_shared_chain,
                          }
        logging.debug('<<< %s' % (text[0]))
        dispatch_table[text[0]](text[2:])

    def _construct_shared_circle(self, data):
        circle_data = json.loads(data)
        pos = circle_data[0]
        radius = circle_data[1]
        density = circle_data[2]
        restitution = circle_data[3]
        friction = circle_data[4]
        self._constructors['Circle'](pos, radius, density, restitution,
                                     friction, share=False)

    def _construct_shared_box(self, data):
        box_data = json.loads(data)
        pos1 = box_data[0]
        pos2 = box_data[1]
        density = box_data[2]
        restitution = box_data[3]
        friction = box_data[4]
        self._constructors['Box'](pos1, pos2, density, restitution,
                                  friction, share=False)

    def _construct_shared_triangle(self, data):
        triangle_data = json.loads(data)
        pos1 = triangle_data[0]
        pos2 = triangle_data[1]
        density = triangle_data[2]
        restitution = triangle_data[3]
        friction = triangle_data[4]
        self._constructors['Triangle'](pos1, pos2, density, restitution,
                                       friction, share=False)

    def _construct_shared_polygon(self, data):
        polygon_data = json.loads(data)
        verticies = polygon_data[0]
        density = polygon_data[1]
        restitution = polygon_data[2]
        friction = polygon_data[3]
        self._constructors['Polygon'](verticies, density, restitution,
                                      friction, share=False)

    def _construct_shared_magicpen(self, data):
        magicpen_data = json.loads(data)
        verticies = magicpen_data[0]
        density = magicpen_data[1]
        restitution = magicpen_data[2]
        friction = magicpen_data[3]
        self._constructors['Magicpen'](verticies, density, restitution,
                                      friction, share=False)

    def _add_shared_joint(self, data):
        joint_data = json.loads(data)
        pos1 = joint_data[0]
        pos2 = joint_data[1]
        self._constructors['Joint'](pos1, pos2, share=False)

    def _add_shared_pin(self, data):
        joint_data = json.loads(data)
        pos = joint_data[0]
        self._constructors['Pin'](pos, share=False)

    def _add_shared_motor(self, data):
        joint_data = json.loads(data)
        pos = joint_data[0]
        speed = joint_data[1]
        self._constructors['Motor'](pos, speed, share=False)

    def _add_shared_track(self, data):
        joint_data = json.loads(data)
        pos = joint_data[0]
        color = joint_data[1]
        self._constructors['Track'](pos, color, share=False)

    def _add_shared_chain(self, data):
        joint_data = json.loads(data)
        pos1 = joint_data[0]
        pos2 = joint_data[1]
        link_length = joint_data[2]
        radius = joint_data[3]
        self._constructors['Chain'](pos1, pos2, link_length, radius,
                                    share=False)

    def send_event(self, text):
        ''' Send event through the tube. '''
        if hasattr(self, 'chattube') and self.chattube is not None:
            logging.debug('>>> %s' % (text[0]))
            self.chattube.SendText(text)


class ChatTube(ExportedGObject):
    ''' Class for setting up tube for sharing '''
    def __init__(self, tube, is_initiator, stack_received_cb):
        super(ChatTube, self).__init__(tube, PATH)
        self.tube = tube
        self.is_initiator = is_initiator  # Are we sharing or joining activity?
        self.stack_received_cb = stack_received_cb
        self.stack = ''

        self.tube.add_signal_receiver(self.send_stack_cb, 'SendText', IFACE,
                                      path=PATH, sender_keyword='sender')

    def send_stack_cb(self, text, sender=None):
        if sender == self.tube.get_unique_name():
            return
        self.stack = text
        self.stack_received_cb(text)

    @signal(dbus_interface=IFACE, signature='s')
    def SendText(self, text):
        self.stack = text
