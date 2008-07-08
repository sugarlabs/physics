import olpcgames
import pygame
from sugar.graphics.toolbutton import ToolButton
from gettext import gettext as _

class PhysicsActivity(olpcgames.PyGameActivity):
    game_name = 'physics'
    game_title = 'Physics'
    game_size = None # olpcgame will choose size

    # custom toolbar
    def build_toolbar(self):
        toolbar = super(PhysicsActivity, self).build_toolbar()
        
        # Add buttons
        toolbar.box = ToolButton('box')
        toolbar.box.set_tooltip(_('Box'))
        toolbar.box.connect('clicked', self._box_cb)
        toolbar.insert(toolbar.box, 2)
        toolbar.box.show()
        
        toolbar.circle = ToolButton('circle')
        toolbar.circle.set_tooltip(_('Circle'))
        toolbar.circle.connect('clicked', self._circle_cb)
        toolbar.insert(toolbar.circle, 2)
        toolbar.circle.show()
        
        toolbar.triangle = ToolButton('triangle')
        toolbar.triangle.set_tooltip(_('Triangle'))
        toolbar.triangle.connect('clicked', self._triangle_cb)
        toolbar.insert(toolbar.triangle, 2)
        toolbar.triangle.show()        
        
        toolbar.polygon = ToolButton('polygon')
        toolbar.polygon.set_tooltip(_('Polygon'))
        toolbar.polygon.connect('clicked', self._polygon_cb)
        toolbar.insert(toolbar.polygon, 2)
        toolbar.polygon.show()

        toolbar.magicpen = ToolButton('magicpen')
        toolbar.magicpen.set_tooltip(_('Magic Pen'))
        toolbar.magicpen.connect('clicked', self._magicpen_cb)
        toolbar.insert(toolbar.magicpen, 2)
        toolbar.magicpen.show()

        toolbar.grab = ToolButton('grab')
        toolbar.grab.set_tooltip(_('Grab'))
        toolbar.grab.connect('clicked', self._grab_cb)
        toolbar.insert(toolbar.grab, 2)
        toolbar.grab.show()

        toolbar.joint = ToolButton('joint')
        toolbar.joint.set_tooltip(_('Joint'))
        toolbar.joint.connect('clicked', self._joint_cb)
        toolbar.insert(toolbar.joint, 2)
        toolbar.joint.show()

        toolbar.destroy = ToolButton('destroy')
        toolbar.destroy.set_tooltip(_('Destroy'))
        toolbar.destroy.connect('clicked', self._destroy_cb)
        toolbar.insert(toolbar.destroy, 2)
        toolbar.destroy.show()
                
        return toolbar

    def _box_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='box'))
    def _circle_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='circle'))
    def _triangle_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='triangle'))
    def _polygon_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='polygon'))
    def _magicpen_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='magicpen'))
    def _grab_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='grab'))
    def _joint_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='joint'))
    def _destroy_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='destroy'))                                              
