import pygtk
pygtk.require('2.0')
import gtk
import hippo

from sugar.activity import activity
import olpcgames

class PhysicsActivity(olpcgames.PyGameActivity):
        
    game_name = 'physics'
    game_title = 'Physics'
    game_handler = 'physics:main'
