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
    game_size = None # olpcgame will choose size
    
    def __init__(self, handle):
        super(PhysicsActivity, self).__init__(handle)
        self.metadata['mime_type'] = 'application/x-physics-activity'

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
        event.retire() # <- without this, title editing stops updating

    # setup the toolbar
    def build_toolbar(self): 
        try:
	    #Use new >= 0.86 toolbar
        self.max_participants = 1
   	    toolbar_box = ToolbarBox()
 	    activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.page.keep.props.accelerator = '<Ctrl><Shift>S'
            activity_button.show()

            create_toolbar = self._create_create_toolbar()
            create_toolbar_button = ToolbarButton(
                            page=create_toolbar,
                            icon_name='toolbar-create')
            create_toolbar.show()
            toolbar_box.toolbar.insert(create_toolbar_button, -1)
            create_toolbar_button.show()

            separator = gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()
	
  	    stop_button = StopButton(self)
            stop_button.props.accelerator = '<Ctrl><Shift>Q'
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()

	    self.set_toolbar_box(toolbar_box)
            toolbar_box.show()
	    return toolbar_box	


        except NameError:       
	    #Use old <= 0.84 toolbar design
            # make a toolbox
            toolbox = activity.ActivityToolbox(self)
         
            # modify the Activity tab
            activity_toolbar = toolbox.get_activity_toolbar()
            activity_toolbar.share.props.visible = False
            self.blocklist = [] 
            # make a 'create' toolbar
            create_toolbar = gtk.Toolbar()
        
            # stop/play button
            self.stop_play_state = True
            self.stop_play = ToolButton('media-playback-stop')
            self.stop_play.set_tooltip(_("Stop"))
            self.stop_play.set_accelerator(_('<ctrl>space'))
            self.stop_play.connect('clicked', self.stop_play_cb)
            create_toolbar.insert(self.stop_play, 0)
            self.stop_play.show()

            separator = gtk.SeparatorToolItem()
            create_toolbar.insert(separator, 1)
            separator.show()
         
            # make + add the component buttons
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
                button.connect('clicked',self.radioClicked)
                create_toolbar.insert(button,-1)    
                button.show()
                self.radioList[button] = c.name
   
                # add the toolbars to the toolbox
                toolbox.add_toolbar(_("Create"),create_toolbar)
        	create_toolbar.show()       
        
        toolbox.show()
        self.set_toolbox(toolbox)
        toolbox.set_current_toolbar(1)
        return activity_toolbar


    def _create_create_toolbar(self):
        create_toolbar = gtk.Toolbar()

        # stop/play button
        self.stop_play_state = True
        self.stop_play = ToolButton('media-playback-stop')
        self.stop_play.set_tooltip(_("Stop"))
        self.stop_play.set_accelerator(_('<ctrl>space'))
        self.stop_play.connect('clicked', self.stop_play_cb)
        create_toolbar.insert(self.stop_play, 0)
        self.stop_play.show()

        separator = gtk.SeparatorToolItem()
        create_toolbar.insert(separator, 1)
        separator.show()

        # make + add the component buttons
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
            button.connect('clicked',self.radioClicked)
            create_toolbar.insert(button,-1)    
            button.show()
            self.radioList[button] = c.name
	return create_toolbar	


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
                    
    def radioClicked(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action=self.radioList[button]))


