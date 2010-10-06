"""
    Physics, a 2D Physics Playground for Kids
    Copyright (C) 2008  Alex Levenson and Brian Jordan

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import tools
import olpcgames
import pygame
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.graphics.toolbutton import ToolButton
from sugar.activity import activity
from gettext import gettext as _
import gtk


try:
    # >= 0.86 toolbars
    from sugar.graphics.toolbarbox import ToolbarButton, ToolbarBox
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
except ImportError:
    # <= 0.84 toolbars
    pass


class PhysicsActivity(olpcgames.PyGameActivity):
    game_name = 'physics'
    game_title = _('Physics')
    game_size = None # Olpcgame will choose size

    def __init__(self, handle):
        super(PhysicsActivity, self).__init__(handle)
        self.metadata['mime_type'] = 'application/x-physics-activity'
        self.connect('visibility-notify-event', self._focus_event)

    def get_preview(self):
        """Custom preview code to get image from pygame.
        """
        surface = pygame.display.get_surface()
        width, height = surface.get_width(), surface.get_height()
        pixbuf = gtk.gdk.pixbuf_new_from_data(pygame.image.tostring(surface, "RGB"),
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

    def write_file(self, file_path):
        """Over-ride olpcgames write_file so that title keeps working.
        """
        event = olpcgames.eventwrap.Event(
            type = pygame.USEREVENT,
            code = olpcgames.FILE_WRITE_REQUEST,
            filename = file_path,
            metadata = self.metadata)
        olpcgames.eventwrap.post(event)
        event.block()
        event.retire() # <- Without this, title editing stops updating

    # Setup the toolbar
    def build_toolbar(self):
        try:
            # Use new >= 0.86 toolbar
            self.max_participants = 1
            toolbar_box = ToolbarBox()
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()

            separator = gtk.SeparatorToolItem()
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()

            self._insert_create_tools(toolbar_box.toolbar)

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_size_request(0, -1)
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()

            stop_button = StopButton(self)
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()
            return toolbar_box

        except NameError:
            # Use old <= 0.84 toolbar design
            toolbox = activity.ActivityToolbox(self)
            activity_toolbar = toolbox.get_activity_toolbar()
            activity_toolbar.share.props.visible = False

            create_toolbar = gtk.Toolbar()
            self._insert_create_tools(create_toolbar)

            toolbox.add_toolbar(_("Create"), create_toolbar)
            create_toolbar.show()
            toolbox.set_current_toolbar(1)

            toolbox.show()
            self.set_toolbox(toolbox)
            return activity_toolbar

    def _insert_create_tools(self, create_toolbar):
        # Stop/play button
        self.stop_play_state = True
        self.stop_play = ToolButton('media-playback-stop')
        self.stop_play.set_tooltip(_("Stop"))
        self.stop_play.set_accelerator(_('<ctrl>space'))
        self.stop_play.connect('clicked', self.stop_play_cb)
        create_toolbar.insert(self.stop_play, -1)
        self.stop_play.show()

        separator = gtk.SeparatorToolItem()
        create_toolbar.insert(separator, -1)
        separator.show()

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
            create_toolbar.insert(button, -1)
            button.show()
            self.radioList[button] = c.name

    def stop_play_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action="stop_start_toggle"))
        self.stop_play_state = not self.stop_play_state
        # Update button
        if self.stop_play_state:
            self.stop_play.set_icon('media-playback-stop')
            self.stop_play.set_tooltip(_("Stop"))
        else:
            self.stop_play.set_icon('media-playback-start')
            self.stop_play.set_tooltip(_("Start"))

    def radioClicked(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action=self.radioList[button]))

    def _focus_event(self, event, data=None):
        """Send focus events to pygame to allow it to more gracefully idle when in the background.
        """
        if data.state == gtk.gdk.VISIBILITY_FULLY_OBSCURED:
            pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action="focus_out"))
        else:
            pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action="focus_in"))
