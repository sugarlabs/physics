'''
This document contains the code for a class that governs the selection of color in the toolbar widget.
'''
from gi.repository import Gtk
from colorButton import ColorToolButton



class ColorPalette(ColorToolButton):

	def __init__(self, activity):
		ColorToolButton.__init__(self)
        	self._activity = activity


