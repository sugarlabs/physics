import olpcgames
import pygame
from sugar.graphics.toolbutton import ToolButton
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
        
        # make a 'create' toolbar
        create_toolbar = gtk.Toolbar()
        
        # make + add the creation buttons
        box = ToolButton('box')
        box.set_tooltip(_("Box"))
        box.connect('clicked',self._box_cb)
        create_toolbar.insert(box,-1)    
        box.show()

        circle = ToolButton('circle')
        circle.set_tooltip(_("Circle"))
        circle.connect('clicked',self._circle_cb)
        create_toolbar.insert(circle,-1)    
        circle.show()

        triangle = ToolButton('triangle')
        triangle.set_tooltip(_("Triangle"))
        triangle.connect('clicked',self._triangle_cb)
        create_toolbar.insert(triangle,-1)    
        triangle.show()
        
        polygon = ToolButton('polygon')
        polygon.set_tooltip(_("Polygon"))
        polygon.connect('clicked',self._polygon_cb)
        create_toolbar.insert(polygon,-1)    
        polygon.show()        
        
        magicpen = ToolButton('magicpen')
        magicpen.set_tooltip(_("Magic Pen"))
        magicpen.connect('clicked',self._magicpen_cb)
        create_toolbar.insert(magicpen,-1)    
        magicpen.show()         
        
        grab = ToolButton('grab')
        grab.set_tooltip(_("Grab"))
        grab.connect('clicked',self._grab_cb)
        create_toolbar.insert(grab,-1)    
        grab.show()         

        joint = ToolButton('joint')
        joint.set_tooltip(_("Joint"))
        joint.connect('clicked',self._joint_cb)
        create_toolbar.insert(joint,-1)    
        joint.show()         

        destroy = ToolButton('destroy')
        destroy.set_tooltip(_("Destroy"))
        destroy.connect('clicked',self._destroy_cb)
        create_toolbar.insert(destroy,-1)    
        destroy.show()         

        # add the toolbars to the toolbox
        toolbox.add_toolbar("Create",create_toolbar)
        create_toolbar.show()        
        
        toolbox.show()
        self.set_toolbox(toolbox)
        return activity_toolbar
        
    def _box_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='box'))    
    def _circle_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='circle'))        
    def _triangle_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='triangle'))        
    def _polygon_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='polygon'))        
    def _magicpen_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='magicpen'))        
    def _grab_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='grab'))        
    def _joint_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='joint'))        
    def _destroy_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='destroy'))                

