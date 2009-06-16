import tools
import olpcgames
import pygame
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.activity import activity
from gettext import gettext as _
import gtk

class PhysicsActivity(olpcgames.PyGameActivity):
    game_name = 'physics'
    game_title = 'Physics'
    game_size = None # olpcgame will choose size

    # setup the toolbar
    def build_toolbar(self):        
        # make a toolbox
        toolbox = activity.ActivityToolbox(self)
         
        # modify the Activity tab
        activity_toolbar = toolbox.get_activity_toolbar()
        activity_toolbar.share.props.visible = False
        self.blocklist = [] 
        # make a 'create' toolbar
        create_toolbar = gtk.Toolbar()
        
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
            button.set_tooltip(_(c.toolTip))
            button.set_accelerator(c.toolAccelerator)
            button.connect('clicked',self.radioClicked)
            create_toolbar.insert(button,-1)    
            button.show()
            self.radioList[button] = c.name

        # add the toolbars to the toolbox
        toolbox.add_toolbar("Create",create_toolbar)
        create_toolbar.show()       
        
        toolbox.show()
        self.set_toolbox(toolbox)
        toolbox.set_current_toolbar(1)
        return activity_toolbar

    def radioClicked(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action=self.radioList[button]))