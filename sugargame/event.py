#
# Copyright (c) 2020 Wade Brainerd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging
from gi.repository import GLib
from gi.repository import Gdk
import pygame
import pygame.event


class _MockEvent(object):
    def __init__(self, keyval):
        self.keyval = keyval


class Translator(object):
    key_trans = {
        'Alt_L': pygame.K_LALT,
        'Alt_R': pygame.K_RALT,
        'Control_L': pygame.K_LCTRL,
        'Control_R': pygame.K_RCTRL,
        'Shift_L': pygame.K_LSHIFT,
        'Shift_R': pygame.K_RSHIFT,
        'Super_L': pygame.K_LSUPER,
        'Super_R': pygame.K_RSUPER,
        'KP_Page_Up': pygame.K_KP9,
        'KP_Page_Down': pygame.K_KP3,
        'KP_End': pygame.K_KP1,
        'KP_Home': pygame.K_KP7,
        'KP_Up': pygame.K_KP8,
        'KP_Down': pygame.K_KP2,
        'KP_Left': pygame.K_KP4,
        'KP_Right': pygame.K_KP6,
        'KP_Next': pygame.K_KP3,
        'KP_Begin': pygame.K_KP5,

    }

    mod_map = {
        pygame.K_LALT: pygame.KMOD_LALT,
        pygame.K_RALT: pygame.KMOD_RALT,
        pygame.K_LCTRL: pygame.KMOD_LCTRL,
        pygame.K_RCTRL: pygame.KMOD_RCTRL,
        pygame.K_LSHIFT: pygame.KMOD_LSHIFT,
        pygame.K_RSHIFT: pygame.KMOD_RSHIFT,
    }

    keys = [
        pygame.K_UNKNOWN,
        pygame.K_BACKSPACE,
        pygame.K_TAB,
        pygame.K_RETURN,
        pygame.K_ESCAPE,
        pygame.K_SPACE,
        pygame.K_EXCLAIM,
        pygame.K_QUOTEDBL,
        pygame.K_HASH,
        pygame.K_DOLLAR,
        pygame.K_PERCENT,
        pygame.K_AMPERSAND,
        pygame.K_QUOTE,
        pygame.K_LEFTPAREN,
        pygame.K_RIGHTPAREN,
        pygame.K_ASTERISK,
        pygame.K_PLUS,
        pygame.K_COMMA,
        pygame.K_MINUS,
        pygame.K_PERIOD,
        pygame.K_SLASH,
        pygame.K_0,
        pygame.K_1,
        pygame.K_2,
        pygame.K_3,
        pygame.K_4,
        pygame.K_5,
        pygame.K_6,
        pygame.K_7,
        pygame.K_8,
        pygame.K_9,
        pygame.K_COLON,
        pygame.K_SEMICOLON,
        pygame.K_LESS,
        pygame.K_EQUALS,
        pygame.K_GREATER,
        pygame.K_QUESTION,
        pygame.K_AT,
        pygame.K_LEFTBRACKET,
        pygame.K_BACKSLASH,
        pygame.K_RIGHTBRACKET,
        pygame.K_CARET,
        pygame.K_UNDERSCORE,
        pygame.K_BACKQUOTE,
        pygame.K_a,
        pygame.K_b,
        pygame.K_c,
        pygame.K_d,
        pygame.K_e,
        pygame.K_f,
        pygame.K_g,
        pygame.K_h,
        pygame.K_i,
        pygame.K_j,
        pygame.K_k,
        pygame.K_l,
        pygame.K_m,
        pygame.K_n,
        pygame.K_o,
        pygame.K_p,
        pygame.K_q,
        pygame.K_r,
        pygame.K_s,
        pygame.K_t,
        pygame.K_u,
        pygame.K_v,
        pygame.K_w,
        pygame.K_x,
        pygame.K_y,
        pygame.K_z,
        pygame.K_DELETE,
        pygame.K_CAPSLOCK,
        pygame.K_F1,
        pygame.K_F2,
        pygame.K_F3,
        pygame.K_F4,
        pygame.K_F5,
        pygame.K_F6,
        pygame.K_F7,
        pygame.K_F8,
        pygame.K_F9,
        pygame.K_F10,
        pygame.K_F11,
        pygame.K_F12,
        pygame.K_PRINT,
        pygame.K_SCROLLOCK,
        pygame.K_BREAK,
        pygame.K_INSERT,
        pygame.K_HOME,
        pygame.K_PAGEUP,
        pygame.K_END,
        pygame.K_PAGEDOWN,
        pygame.K_RIGHT,
        pygame.K_LEFT,
        pygame.K_DOWN,
        pygame.K_UP,
        pygame.K_NUMLOCK,
        pygame.K_KP_DIVIDE,
        pygame.K_KP_MULTIPLY,
        pygame.K_KP_MINUS,
        pygame.K_KP_PLUS,
        pygame.K_KP_ENTER,
        pygame.K_KP1,
        pygame.K_KP2,
        pygame.K_KP3,
        pygame.K_KP4,
        pygame.K_KP5,
        pygame.K_KP6,
        pygame.K_KP7,
        pygame.K_KP8,
        pygame.K_KP9,
        pygame.K_KP0,
        pygame.K_KP_PERIOD,
        pygame.K_POWER,
        pygame.K_KP_EQUALS,
        pygame.K_F13,
        pygame.K_F14,
        pygame.K_F15,
        pygame.K_HELP,
        pygame.K_MENU,
        pygame.K_SYSREQ,
        pygame.K_CLEAR,
        pygame.K_CURRENCYUNIT,
        pygame.K_CURRENCYSUBUNIT,
        pygame.K_LCTRL,
        pygame.K_LSHIFT,
        pygame.K_LALT,
        pygame.K_LMETA,
        pygame.K_RCTRL,
        pygame.K_RSHIFT,
        pygame.K_RALT,
        pygame.K_RMETA,
        pygame.K_MODE,
        pygame.K_AC_BACK
    ]

    def __init__(self, activity, inner_evb):
        """Initialise the Translator with the windows to which to listen"""
        self._activity = activity
        self._inner_evb = inner_evb

        # Enable events
        # (add instead of set here because the main window is already realized)
        self._activity.add_events(
            Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.KEY_RELEASE_MASK |
            Gdk.EventMask.VISIBILITY_NOTIFY_MASK
        )

        self._inner_evb.set_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.POINTER_MOTION_HINT_MASK |
            Gdk.EventMask.BUTTON_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        self._activity.set_can_focus(True)
        self._inner_evb.set_can_focus(True)

        # Callback functions to link the event systems
        self._activity.connect('unrealize', self._quit_cb)
        self._activity.connect('visibility-notify-event', self._visibility_cb)
        self._inner_evb.connect('size-allocate', self._resize_cb)
        self._inner_evb.connect('key-press-event', self._keydown_cb)
        self._inner_evb.connect('key-release-event', self._keyup_cb)
        self._inner_evb.connect('button-press-event', self._mousedown_cb)
        self._inner_evb.connect('button-release-event', self._mouseup_cb)
        self._inner_evb.connect('motion-notify-event', self._mousemove_cb)
        self._inner_evb.connect('screen-changed', self._screen_changed_cb)

        # Internal data
        self.__button_state = [0, 0, 0]
        self.__mouse_pos = (0, 0)
        self.__repeat = (None, None)
        self.__held = set()
        self.__held_time_left = {}
        self.__held_last_time = {}
        self.__tick_id = None
        self.__keystate = dict((i, False) for i in self.keys)

    def hook_pygame(self):
        pygame.key.get_pressed = self._get_pressed
        pygame.key.set_repeat = self._set_repeat
        pygame.mouse.get_pressed = self._get_mouse_pressed
        pygame.mouse.get_pos = self._get_mouse_pos

    def update_display(self):
        if pygame.display.get_init():
            pygame.event.post(pygame.event.Event(pygame.VIDEOEXPOSE))

    def _resize_cb(self, widget, allocation):
        if pygame.display.get_init():
            evt = pygame.event.Event(pygame.VIDEORESIZE,
                                     size=(allocation.width, allocation.height),
                                     width=allocation.width, height=allocation.height)
            pygame.event.post(evt)
        return False  # continue processing

    def _screen_changed_cb(self, widget, previous_screen):
        self.update_display()

    def _quit_cb(self, data=None):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _visibility_cb(self, widget, event):
        self.update_display()
        return False

    def _keydown_cb(self, widget, event):
        key = event.keyval
        if key in self.__held:
            return True
        else:
            if self.__repeat[0] is not None:
                self.__held_last_time[key] = pygame.time.get_ticks()
                self.__held_time_left[key] = self.__repeat[0]
            self.__held.add(key)

        return self._keyevent(widget, event, pygame.KEYDOWN)

    def _keyup_cb(self, widget, event):
        key = event.keyval
        if self.__repeat[0] is not None:
            if key in self.__held:
                # This is possibly false if set_repeat()
                # is called with a key held
                del self.__held_time_left[key]
                del self.__held_last_time[key]
        self.__held.discard(key)

        return self._keyevent(widget, event, pygame.KEYUP)

    def _keymods(self):
        mod = 0
        for key_val, mod_val in self.mod_map.items():
            mod |= self.__keystate[key_val] and mod_val
        return mod

    def _keyevent(self, widget, event, type):
        key = Gdk.keyval_name(event.keyval)
        if key is None:
            # No idea what this key is.
            return False

        keycode = None
        if key in self.key_trans:
            keycode = self.key_trans[key]
        elif hasattr(pygame, 'K_' + key.upper()):
            keycode = getattr(pygame, 'K_' + key.upper())
        elif hasattr(pygame, 'K_' + key.lower()):
            keycode = getattr(pygame, 'K_' + key.lower())
        elif key == 'XF86Start':
            # view source request, specially handled...
            self._activity.view_source()
        else:
            logging.error('Key %s unrecognized' % key)

        if keycode is not None:
            if type == pygame.KEYDOWN:
                mod = self._keymods()
            self.__keystate[keycode] = type == pygame.KEYDOWN
            if type == pygame.KEYUP:
                mod = self._keymods()
            ukey = chr(Gdk.keyval_to_unicode(event.keyval))
            if ukey == '\000':
                ukey = ''
            evt = pygame.event.Event(type, key=keycode, unicode=ukey, mod=mod)
            self._post(evt)

        return True

    def _get_pressed(self):
        return list(self.__keystate.values())

    def _get_mouse_pressed(self):
        return self.__button_state

    def _mousedown_cb(self, widget, event):
        self.__button_state[event.button - 1] = 1
        return self._mouseevent(widget, event, pygame.MOUSEBUTTONDOWN)

    def _mouseup_cb(self, widget, event):
        self.__button_state[event.button - 1] = 0
        return self._mouseevent(widget, event, pygame.MOUSEBUTTONUP)

    def _mouseevent(self, widget, event, type):
        evt = pygame.event.Event(type, button=event.button, pos=(event.x,
                                                                 event.y))
        self._post(evt)
        return True

    def _mousemove_cb(self, widget, event):
        # From http://www.learningpython.com/2006/07/25/writing-a-custom-widget-using-pygtk/
        # if this is a hint, then let's get all the necessary
        # information, if not it's all we need.
        if event.is_hint:
            win, x, y, state = event.window.get_device_position(event.device)
        else:
            x = event.x
            y = event.y
            state = event.get_state()

        rel = (x - self.__mouse_pos[0], y - self.__mouse_pos[1])
        self.__mouse_pos = (x, y)

        self.__button_state = [
            state & Gdk.ModifierType.BUTTON1_MASK and 1 or 0,
            state & Gdk.ModifierType.BUTTON2_MASK and 1 or 0,
            state & Gdk.ModifierType.BUTTON3_MASK and 1 or 0,
        ]

        evt = pygame.event.Event(pygame.MOUSEMOTION,
                                 pos=self.__mouse_pos, rel=rel,
                                 buttons=self.__button_state)
        self._post(evt)
        return True

    def _tick_cb(self):
        cur_time = pygame.time.get_ticks()
        for key in self.__held:
            delta = cur_time - self.__held_last_time[key]
            self.__held_last_time[key] = cur_time

            self.__held_time_left[key] -= delta
            if self.__held_time_left[key] <= 0:
                self.__held_time_left[key] = self.__repeat[1]
                self._keyevent(None, _MockEvent(key), pygame.KEYDOWN)

        return True

    def _set_repeat(self, delay=None, interval=None):
        if delay is not None and self.__repeat[0] is None:
            self.__tick_id = GLib.timeout_add(10, self._tick_cb)
        elif delay is None and self.__repeat[0] is not None:
            GLib.source_remove(self.__tick_id)
        self.__repeat = (delay, interval)

    def _get_mouse_pos(self):
        return self.__mouse_pos

    def _post(self, evt):
        try:
            pygame.event.post(evt)
        except pygame.error as e:
            if str(e) == 'video system not initialized':
                pass
            elif str(e) == 'Event queue full':
                logging.error("Event queue full!")
                pass
            else:
                raise e
