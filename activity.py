import tools
import olpcgames
import pygame
from sugar.graphics.radiotoolbutton import RadioToolButton
from sugar.graphics.toolbutton import ToolButton
from sugar.activity import activity
from gettext import gettext as _
import gtk

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