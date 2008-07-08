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
        toolbar.button1 = ToolButton('activity-button1')
        toolbar.button1.set_tooltip(_('Button One'))
        toolbar.button1.connect('clicked', self._button1_cb)
        toolbar.insert(toolbar.button1, 2)
        toolbar.button1.show()
        
        toolbar.button2 = ToolButton('activity-button2')
        toolbar.button2.set_tooltip(_('button-2'))
        toolbar.button2.connect('clicked', self._button2_cb)
        toolbar.insert(toolbar.button2, 2)
        toolbar.button2.show()
        return toolbar

    def _button1_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='button1'))
        
    def _button2_cb(self, button):
        pygame.event.post(olpcgames.eventwrap.Event(pygame.USEREVENT, action='button2'))
