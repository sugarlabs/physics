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
        
        # make a 'create' toolbar
        create_toolbar = gtk.Toolbar()
        
        # make + add the creation buttons
        self.box = RadioToolButton(named_icon='box')
        self.box.set_tooltip(_("Box"))
        self.box.connect('clicked',self._box_cb)
        create_toolbar.insert(self.box,-1)    
        self.box.show()

        self.circle = RadioToolButton(group=self.box, named_icon='circle')
        self.circle.set_tooltip(_("Circle"))
        self.circle.connect('clicked',self._circle_cb)
        create_toolbar.insert(self.circle,-1)    
        self.circle.show()

        self.triangle = RadioToolButton(group=self.box, named_icon='triangle')
        self.triangle.set_tooltip(_("Triangle"))
        self.triangle.connect('clicked',self._triangle_cb)
        create_toolbar.insert(self.triangle,-1)    
        self.triangle.show()
        
        self.polygon = RadioToolButton(group=self.box, named_icon='polygon')
        self.polygon.set_tooltip(_("Polygon"))
        self.polygon.connect('clicked',self._polygon_cb)
        create_toolbar.insert(self.polygon,-1)    
        self.polygon.show()        
        
        self.magicpen = RadioToolButton(group=self.box, named_icon='magicpen')
        self.magicpen.set_tooltip(_("Magic Pen"))
        self.magicpen.connect('clicked',self._magicpen_cb)
        create_toolbar.insert(self.magicpen,-1)    
        self.magicpen.show()         
        
        self.grab = RadioToolButton(group=self.box, named_icon='grab')
        self.grab.set_tooltip(_("Grab"))
        self.grab.connect('clicked',self._grab_cb)
        create_toolbar.insert(self.grab,-1)    
        self.grab.show()         

        self.joint = RadioToolButton(group=self.box, named_icon='joint')
        self.joint.set_tooltip(_("Joint"))
        self.joint.connect('clicked',self._joint_cb)
        create_toolbar.insert(self.joint,-1)    
        self.joint.show()         

        self.destroy = RadioToolButton(group=self.box, named_icon='destroy')
        self.destroy.set_tooltip(_("Destroy"))
        self.destroy.connect('clicked',self._destroy_cb)
        create_toolbar.insert(self.destroy,-1)    
        self.destroy.show()         

        # add the toolbars to the toolbox
        toolbox.add_toolbar("Create",create_toolbar)
        create_toolbar.show()        
        
        toolbox.show()
        self.set_toolbox(toolbox)
        return activity_toolbar
        
    def _box_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='box'))    
        #self.box.do_toggled(self.box)
    
    def _circle_cb(self,button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='circle'))
        #self.circle.set_active(True)
        
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

