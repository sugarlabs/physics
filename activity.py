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
import tempfile
import json
import logging
import glob
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
from sugar3.graphics.objectchooser import ObjectChooser
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.alert import ConfirmationAlert
from sugar3.graphics.alert import NotifyAlert
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.style import GRID_CELL_SIZE
from sugar3.datastore import datastore

from colorbutton import ColorToolButton
try:
    from sugar3.presence.wrapper import CollabWrapper
except ImportError:
    from collabwrapper import CollabWrapper

import tools
import physics

# For some reason increasing FPS decreases execution speed :/
SLOWEST_FPS = 90
SLOW_FPS = 70
FAST_FPS = 50


class PhysicsActivity(activity.Activity):

    def __init__(self, handle):
        super(PhysicsActivity, self).__init__(handle)
        self._collab = CollabWrapper(self)
        self._collab.message.connect(self.__message_cb)
        self.metadata['mime_type'] = 'application/x-physics-activity'
        self.add_events(Gdk.EventMask.ALL_EVENTS_MASK |
                        Gdk.EventMask.VISIBILITY_NOTIFY_MASK)

        self.connect('visibility-notify-event', self._focus_event)
        self.connect('window-state-event', self._window_event)

        self.game_canvas = sugargame.canvas.PygameCanvas(self)
        self.game = physics.main(self)

        self.preview = None
        self._sample_window = None

        self._fixed = Gtk.Fixed()
        self._fixed.put(self.game_canvas, 0, 0)

        w = Gdk.Screen.width()
        h = Gdk.Screen.height() - 2 * GRID_CELL_SIZE

        self.game_canvas.set_size_request(w, h)

        self._constructors = {}
        self.build_toolbar()

        self.set_canvas(self._fixed)
        Gdk.Screen.get_default().connect('size-changed',
                                         self.__configure_cb)

        logging.debug(os.path.join(
                      activity.get_activity_root(), 'data', 'data'))
        self.game_canvas.run_pygame(self.game.run)
        self.show_all()
        self._collab.setup()

    def __configure_cb(self, event):
        ''' Screen size has changed '''
        self.write_file(os.path.join(
                        activity.get_activity_root(), 'data', 'data'))
        w = Gdk.Screen.width()
        h = Gdk.Screen.height() - 2 * GRID_CELL_SIZE
        pygame.display.set_mode((w, h),
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
        return self.game_canvas.get_preview()

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

        color = ColorToolButton('color')
        color.connect('notify::color', self.__color_notify_cb)
        toolbar_box.toolbar.insert(color, -1)
        color.show()

        random = ToggleToolButton('colorRandom')
        random.set_tooltip(_('Toggle random color'))
        toolbar_box.toolbar.insert(random, -1)
        random.set_active(True)
        random.connect('toggled', self.__random_toggled_cb)
        random.show()

        color.random = random
        random.color = color

        random.timeout_id = GObject.timeout_add(100, self.__timeout_cb, random)

        self._insert_stop_play_button(toolbar_box.toolbar)

        clear_trace = ToolButton('clear-trace')
        clear_trace.set_tooltip(_('Clear Trace Marks'))
        clear_trace.set_accelerator(_('<ctrl>x'))
        clear_trace.connect('clicked', self.clear_trace_cb)
        clear_trace.set_sensitive(False)
        toolbar_box.toolbar.insert(clear_trace, -1)
        clear_trace.show()
        self.clear_trace = clear_trace

        self._insert_clear_all_button(toolbar_box.toolbar)

        load_example = ToolButton('load-sample')
        load_example.set_tooltip(_('Show sample projects'))
        load_example.connect('clicked', self._create_store)

        toolbar_box.toolbar.insert(Gtk.SeparatorToolItem(), -1)
        toolbar_box.toolbar.insert(load_example, -1)
        load_example.show()

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

        load_project = ToolButton('load-project')
        load_project.set_tooltip(_('Load project from journal'))
        load_project.connect('clicked', self._load_project)
        activity_button.props.page.insert(load_project, -1)
        load_project.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show_all()
        create_toolbar.set_expanded(True)
        return toolbar_box

    def __color_notify_cb(self, button, pdesc):
        """ when a color is chosen;
        change world object add color,
        and change color of buttons. """

        color = button.get_color()
        self._set_color(color)
        button.random.set_active(False)
        button.random.get_icon_widget().set_stroke_color(self._rgb8x(color))

    def __random_toggled_cb(self, random):
        if random.props.active:
            self._random_on(random)
        else:
            self._random_off(random)

    def _random_on(self, random):
        """ when random is turned on;
        reset world object add color,
        and begin watching for changed world object add color. """

        self.game.world.add.reset_color()

        if random.timeout_id is None:
            random.timeout_id = GObject.timeout_add(100, self.__timeout_cb,
                                                    random)
            self.__timeout_cb(random)

    def _random_off(self, random):
        """ when random is turned off;
        change world object add color back to chosen color,
        change color of buttons,
        and stop watching for changed world object add color. """

        color = random.color.get_color()
        self._set_color(color)
        random.get_icon_widget().set_stroke_color(self._rgb8x(color))

        if random.timeout_id is not None:
            GObject.source_remove(random.timeout_id)
            random.timeout_id = None

    def __timeout_cb(self, random):
        """ copy the next color to the random button stroke color. """
        if hasattr(self.game, "world"):
            color = self.game.world.add.next_color()
            random.get_icon_widget().set_stroke_color('#%.2X%.2X%.2X' % color)
        return True

    def _set_color(self, color):
        """ set world object add color. """
        self.game.world.add.set_color(self._rgb8(color))

    def _rgb8x(self, color):
        """ convert a Gdk.Color into hex triplet. """
        return '#%.2X%.2X%.2X' % self._rgb8(color)

    def _rgb8(self, color):
        """ convert a Gdk.Color into an 8-bit RGB tuple. """
        return (color.red / 256, color.green / 256, color.blue / 256)

    def can_close(self):
        self.preview = self.get_preview()
        self.game.loop = False
        return True

    def _insert_stop_play_button(self, toolbar):

        self.stop_play_toolbar = ToolbarButton()
        st_toolbar = self.stop_play_toolbar
        st_toolbar.props.page = Gtk.Toolbar()
        st_toolbar.props.icon_name = 'media-playback-stop'

        self.stop_play_state = True
        self.stop_play = ToolButton('media-playback-stop')
        self.stop_play.set_tooltip(_('Stop'))
        self.stop_play.set_accelerator(_('<ctrl>space'))
        self.stop_play.connect('clicked', self.stop_play_cb)
        self._insert_item(st_toolbar, self.stop_play)
        self.stop_play.show()

        slowest_button = RadioToolButton(group=None)
        slowest_button.set_icon_name('slow-walk-milton-raposo')
        slowest_button.set_tooltip(_('Run slower'))
        slowest_button.connect('clicked', self._set_fps_cb, SLOWEST_FPS)
        self._insert_item(st_toolbar, slowest_button)
        slowest_button.show()

        slow_button = RadioToolButton(group=slowest_button)
        slow_button.set_icon_name('walking')
        slow_button.set_tooltip(_('Run slow'))
        slow_button.connect('clicked', self._set_fps_cb, SLOW_FPS)
        self._insert_item(st_toolbar, slow_button)
        slow_button.show()

        fast_button = RadioToolButton(group=slowest_button)
        fast_button.set_icon_name('running')
        fast_button.set_tooltip('Run fast')
        fast_button.connect('clicked', self._set_fps_cb, FAST_FPS)
        self._insert_item(st_toolbar, fast_button)
        fast_button.show()
        fast_button.set_active(True)

        toolbar.insert(self.stop_play_toolbar, -1)
        self.stop_play_toolbar.show_all()

    def _set_fps_cb(self, button, value):
        self.game.set_game_fps(value)

    def _insert_clear_all_button(self, toolbar):
        self.clear_all = ToolButton('clear_all')
        self.clear_all.set_tooltip(_('Erase All'))
        self.clear_all.set_accelerator(_('<ctrl>a'))
        self.clear_all.connect('clicked', self.clear_all_cb)
        toolbar.insert(self.clear_all, -1)
        self.clear_all.set_sensitive(False)
        self.clear_all.show()

    def _insert_item(self, toolbar, item, pos=-1):
        if hasattr(toolbar, 'insert'):
            toolbar.insert(item, pos)
        else:
            toolbar.props.page.insert(item, pos)

    def _insert_create_tools(self, create_toolbar):
        # Make + add the component buttons
        self.radioList = {}
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
            self._insert_item(create_toolbar, button, -1)
            button.show()
            self.radioList[button] = c.name
            if hasattr(c, 'constructor'):
                self._constructors[c.name] = \
                    self.game.toolList[c.name].constructor

    def __icon_path(self, name):
        activity_path = activity.get_bundle_path()
        icon_path = os.path.join(activity_path, 'icons',
                                 name + '.svg')
        return icon_path

    def _build_palette(self, tool):
        if tool.palette_enabled:
            if tool.palette_mode == tools.PALETTE_MODE_ICONS:
                grid = Gtk.Grid()
                for s, settings in enumerate(tool.palette_settings):
                    self.game.toolList[tool.name].buttons.append([])
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
                            button.set_icon_name(settings['icons'][i] +
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
                # See http://bugs.sugarlabs.org/ticket/305
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

            self.stop_play_toolbar.set_icon_name('media-playback-stop')
        else:
            self.stop_play.set_icon_name('media-playback-start')
            self.stop_play.set_tooltip(_('Start'))

            self.stop_play_toolbar.set_icon_name('media-playback-start')

    def clear_all_cb(self, button):
        def clear_all_alert_cb(alert, response_id):
            self.remove_alert(alert)
            if response_id is Gtk.ResponseType.OK:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                     action='clear_all'))
        if len(self.game.world.world.bodies) > 2:
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

        self.game.world.json_save(file_path)

        jobject.set_file_path(file_path)
        datastore.write(jobject)

    def _window_event(self, window, event):
        ''' Send focus out event to pygame when switching to a desktop
        view. '''
        if event.changed_mask & Gdk.WindowState.ICONIFIED:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT,
                                                 action='focus_out'))

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

    def __message_cb(self, collab, buddy, msg):
        ''' Data is passed as tuples: cmd:text '''
        action = msg.get('action')
        if action != 'text':
            return

        text = msg['text']
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
        vertices = polygon_data[0]
        density = polygon_data[1]
        restitution = polygon_data[2]
        friction = polygon_data[3]
        self._constructors['Polygon'](vertices, density, restitution,
                                      friction, share=False)

    def _construct_shared_magicpen(self, data):
        magicpen_data = json.loads(data)
        vertices = magicpen_data[0]
        density = magicpen_data[1]
        restitution = magicpen_data[2]
        friction = magicpen_data[3]
        self._constructors['Magicpen'](vertices, density, restitution,
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
        vertices = joint_data[0]
        link_length = joint_data[1]
        radius = joint_data[2]
        self._constructors['Chain'](vertices, link_length, radius,
                                    share=False)

    def send_event(self, text):
        self._collab.post(dict(action='text', text=text))

    def _load_project(self, button):
        chooser = ObjectChooser(parent=self)
        result = chooser.run()
        if result == Gtk.ResponseType.ACCEPT:
            dsobject = chooser.get_selected_object()
            file_path = dsobject.get_file_path()
            self.__load_game(file_path, True)
            chooser.destroy()

    def __load_game(self, file_path, journal=False):
        confirmation_alert = ConfirmationAlert()
        confirmation_alert.props.title = _('Are You Sure?')
        confirmation_alert.props.msg = \
            _('All your work will be discarded. This cannot be undone!')

        def action(alert, response):
            self.remove_alert(alert)
            if response is not Gtk.ResponseType.OK:
                return

            try:
                f = open(file_path, 'r')
                # Test if the file is valid project.
                json.loads(f.read())
                f.close()

                self.read_file(file_path)
                self.game.run(True)
            except:
                title = _('Load project from journal')
                if not journal:
                    title = _('Load example')
                msg = _(
                    'Error: Cannot open Physics project from this file.')
                alert = NotifyAlert(5)
                alert.props.title = title
                alert.props.msg = msg
                alert.connect(
                    'response',
                    lambda alert,
                    response: self.remove_alert(alert))
                self.add_alert(alert)

        confirmation_alert.connect('response', action)
        self.add_alert(confirmation_alert)

    def _create_store(self, widget=None):
        width = Gdk.Screen.width() / 4
        height = Gdk.Screen.height() / 4

        if self._sample_window is None:
            self._sample_box = Gtk.EventBox()

            vbox = Gtk.VBox()
            self._sample_window = Gtk.ScrolledWindow()
            self._sample_window.set_policy(Gtk.PolicyType.NEVER,
                                           Gtk.PolicyType.AUTOMATIC)
            self._sample_window.set_border_width(4)
            w = Gdk.Screen.width() / 2
            h = Gdk.Screen.height() / 2
            self._sample_window.set_size_request(w, h)
            self._sample_window.show()

            store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)

            icon_view = Gtk.IconView()
            icon_view.set_model(store)
            icon_view.set_selection_mode(Gtk.SelectionMode.SINGLE)
            icon_view.connect('selection-changed', self._sample_selected,
                              store)
            icon_view.set_pixbuf_column(0)
            icon_view.grab_focus()
            self._sample_window.add(icon_view)
            icon_view.show()
            self._fill_samples_list(store)

            title = Gtk.HBox()
            title_label = Gtk.Label(_("Select a sample..."))
            separator = Gtk.HSeparator()
            separator.props.expand = True
            separator.props.visible = False

            btn = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
            btn.connect('clicked', lambda button: self._sample_box.hide())

            title.pack_start(title_label, False, False, 5)
            title.pack_start(separator, False, False, 0)
            title.pack_end(btn, False, False, 0)

            vbox.pack_start(title, False, False, 5)
            vbox.pack_end(self._sample_window, True, True, 0)

            self._sample_box.add(vbox)

            self._fixed.put(self._sample_box, width, height)

        if self._sample_window:
            # Remove and add again. Maybe its on portrait mode.
            self._fixed.remove(self._sample_box)
            self._fixed.put(self._sample_box, width, height)

        self._sample_box.show_all()

    def _get_selected_path(self, widget, store):
        try:
            iter_ = store.get_iter(widget.get_selected_items()[0])
            image_path = store.get(iter_, 1)[0]

            return image_path, iter_
        except:
            return None

    def _sample_selected(self, widget, store):
        selected = self._get_selected_path(widget, store)

        if selected is None:
            self._selected_sample = None
            self._sample_box.hide()
            return

        image_path, _iter = selected
        iter_ = store.get_iter(widget.get_selected_items()[0])
        image_path = store.get(iter_, 1)[0]

        self._selected_sample = image_path
        self._sample_box.hide()

        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        GObject.idle_add(self._sample_loader)

    def _sample_loader(self):
        # Convert from thumbnail path to sample path
        basename = os.path.basename(self._selected_sample)[:-4]
        file_path = os.path.join(activity.get_bundle_path(),
                                 'samples', basename + '.json')
        self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.LEFT_PTR))
        self.__load_game(file_path)

    def _fill_samples_list(self, store):
        '''
        Append images from the artwork_paths to the store.
        '''
        for filepath in self._scan_for_samples():
            pixbuf = None
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filepath, 100, 100)
            store.append([pixbuf, filepath])

    def _scan_for_samples(self):
        samples = sorted(
            glob.glob(
                os.path.join(
                    activity.get_bundle_path(),
                    'samples',
                    'thumbnails',
                    '*.png')))
        return samples
