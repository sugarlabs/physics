import os
from gi.repository import Gtk
from gi.repository import GObject
from sugar3.activity.activity import PREVIEW_SIZE
import pygame
import event

CANVAS = None

class PygameCanvas(Gtk.EventBox):

    """
    mainwindow is the activity intself.
    """
    def __init__(self, mainwindow, pointer_hint = True):
        GObject.GObject.__init__(self)

        global CANVAS
        assert CANVAS == None, "Only one PygameCanvas can be created, ever."
        CANVAS = self

        # Initialize Events translator before widget gets "realized".
        self.translator = event.Translator(mainwindow, self)

        self._mainwindow = mainwindow

        self.set_can_focus(True)

        self._socket = Gtk.Socket()
        self.add(self._socket)

        self._initialized = False

        self.show_all()

    def get_preview(self):
        """
        Return preview of main surface
        How to use in activity:
            def get_preview(self):
                return self.game_canvas.get_preview()
        """

        _tmp_dir = os.path.join(self._mainwindow.get_activity_root(),
            'tmp')
        _file_path = os.path.join(_tmp_dir, 'preview.png')

        width = PREVIEW_SIZE[0]
        height = PREVIEW_SIZE[1]
        _surface = pygame.transform.scale(self._screen, (width, height))
        pygame.image.save(_surface, _file_path)

        f = open(_file_path, 'r')
        preview = f.read()
        f.close()
        os.remove(_file_path)
	
        return preview

    def run_pygame(self, main_fn):
        # Run the main loop after a short delay.  The reason for the
        # delay is that the Sugar activity is not properly created
        # until after its constructor returns.  If the Pygame main
        # loop is called from the activity constructor, the
        # constructor never returns and the activity freezes.
        GObject.idle_add(self._run_pygame_cb, main_fn)

    def _run_pygame_cb(self, main_fn):
        # PygameCanvas.run_pygame can only be called once
        if self._initialized:
            return

        # Preinitialize Pygame with the X window ID.
        os.environ['SDL_WINDOWID'] = str(self._socket.get_id())
        if pygame.display.get_surface() is not None:
            pygame.display.quit()
        pygame.init()

        # Restore the default cursor.
        self._socket.props.window.set_cursor(None)

        # Initialize the Pygame window.
        r = self.get_allocation()
        # pygame.display.set_mode((r.width, r.height), pygame.RESIZABLE)
        self._screen = pygame.display.set_mode((r.width, r.height),
            pygame.RESIZABLE)

        # Hook certain Pygame functions with GTK equivalents.
        self.translator.hook_pygame()

        # Run the Pygame main loop.
        main_fn()

        self._initialized = True
        return False

    def get_pygame_widget(self):
        return self._socket
