import os
from gi.repository import Gtk
from gi.repository import GLib
from sugar3.activity.activity import PREVIEW_SIZE
import pygame
import sugargame.event as event

CANVAS = None


class PygameCanvas(Gtk.EventBox):
    def __init__(self, activity, main=None, modules=[pygame]):
        Gtk.EventBox.__init__(self)

        global CANVAS
        assert CANVAS is None, "Only one PygameCanvas can be created, ever."
        CANVAS = self

        # Initialize Events translator before widget gets "realized".
        self.translator = event.Translator(activity, self)

        self._activity = activity
        self._main = main
        self._modules = modules

        self.set_can_focus(True)

        self._socket = Gtk.Socket()
        self._socket.connect('realize', self._realize_cb)
        self.add(self._socket)

        self.show_all()

    def _realize_cb(self, widget):

        # Preinitialize Pygame with the X window ID.
        os.environ['SDL_WINDOWID'] = str(widget.get_id())
        for module in self._modules:
            module.init()

        # Restore the default cursor.
        widget.props.window.set_cursor(None)

        # Confine the Pygame surface to the canvas size
        r = self.get_allocation()
        self._screen = pygame.display.set_mode((r.width, r.height),
                                               pygame.RESIZABLE)

        # Hook certain Pygame functions with GTK equivalents.
        self.translator.hook_pygame()

        # Call the caller's main loop as an idle source
        if self._main:
            GLib.idle_add(self._main)

    def get_pygame_widget(self):
        return self._socket

    def get_preview(self):
        """
        Return preview of main surface
        How to use in activity:
            def get_preview(self):
                return self.game_canvas.get_preview()
        """

        if not hasattr(self, '_screen'):
            return None

        _tmp_dir = os.path.join(self._activity.get_activity_root(),
                                'tmp')
        _file_path = os.path.join(_tmp_dir, 'preview.png')

        width = PREVIEW_SIZE[0]
        height = PREVIEW_SIZE[1]
        _surface = pygame.transform.scale(self._screen, (width, height))
        pygame.image.save(_surface, _file_path)

        f = open(_file_path, 'rb')
        preview = f.read()
        f.close()
        os.remove(_file_path)

        return preview
