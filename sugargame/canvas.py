import os
import gtk
import gobject
import pygame
import event

CANVAS = None

class PygameCanvas(gtk.EventBox):
    
    """
    mainwindow is the activity intself.
    """
    def __init__(self, mainwindow, pointer_hint = True):
        gtk.EventBox.__init__(self)

        global CANVAS
        assert CANVAS == None, "Only one PygameCanvas can be created, ever."
        CANVAS = self

        # Initialize Events translator before widget gets "realized".
        self.translator = event.Translator(mainwindow, self)
        
        self._mainwindow = mainwindow

        self.set_flags(gtk.CAN_FOCUS)
        
        self._socket = gtk.Socket()
        self.add(self._socket)
        self.show_all()

    def run_pygame(self, main_fn):
        # Run the main loop after a short delay.  The reason for the delay is that the
        # Sugar activity is not properly created until after its constructor returns.
        # If the Pygame main loop is called from the activity constructor, the 
        # constructor never returns and the activity freezes.
        gobject.idle_add(self._run_pygame_cb, main_fn)

    def _run_pygame_cb(self, main_fn):
        assert pygame.display.get_surface() is None, "PygameCanvas.run_pygame can only be called once."
        
        # Preinitialize Pygame with the X window ID.
        assert pygame.display.get_init() == False, "Pygame must not be initialized before calling PygameCanvas.run_pygame."
        os.environ['SDL_WINDOWID'] = str(self._socket.get_id())
        pygame.init()
        
        # Restore the default cursor.
        self._socket.window.set_cursor(None)

        # Initialize the Pygame window.
        r = self.get_allocation()
        pygame.display.set_mode((r.width, r.height), pygame.RESIZABLE)

        # Hook certain Pygame functions with GTK equivalents.
        self.translator.hook_pygame()

        # Run the Pygame main loop.
        main_fn()
        return False

    def get_pygame_widget(self):
        return self._socket
