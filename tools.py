# -*- coding: utf-8 -*-
# Physics, a 2D Physics Playground for Kids

# Copyright (C) 2008  Alex Levenson and Brian Jordan
# Copyright (C) 2012  Daniel Francis
# Copyright (C) 2012-14  Walter Bender
# Copyright (C) 2013,14  Sai Vineet
# Copyright (C) 2012-14  Sugar Labs

#  This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import math
import logging
import pygame
from shutil import copy
from gettext import gettext as _

from pygame.locals import *
from helpers import *

from sugar3.activity import activity

PALETTE_MODE_SLIDER_ICON = 0
PALETTE_MODE_ICONS = 1
PALETTE_MODE_SLIDER_LABEL = 2
PALETTE_ICON_OBJECT_SETTINGS = [
    {
        'name': 'density',
        'icon_count': 3,
        'icons': ['feather', 'wood', 'anvil'],
        'icon_values': [0.5, 1.0, 10.0],
        'active': 'wood'
    },
    {
        'name': 'restitution',
        'icon_count': 3,
        'icons': ['basketball', 'tennis-ball', 'bowling-ball'],
        'icon_values': [1, 0.16, 0.01],
        'active': 'tennis-ball'
    },
    {
        'name': 'friction',
        'icon_count': 3,
        'icons': ['ice-skate', 'shoe', 'sneaker'],
        'icon_values': [0.5, 1, 2],
        'active': 'grass'
    }]
PALETTE_OBJECT_DATA = {
    'density': 1.0,
    'restitution': 0.16,
    'friction': 1
}


# Tools that can be superlcassed
class Tool(object):
    name = 'Tool'
    icon = 'icon'
    toolTip = 'Tool Tip'
    toolAccelerator = None
    palette_enabled = False
    palette_mode = None
    palette_settings = None
    palette_data = None

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.name = self.__class__.name

    def handleEvents(self, event):
        handled = True
        # Default event handling
        if event.type == USEREVENT:
            if hasattr(event, 'action'):
                if event.action == 'stop_start_toggle':
                    # Stop/start simulation
                    toggle = self.game.world.run_physics
                    self.game.world.run_physics = not toggle
                elif event.action == 'clear_all':
                    # Get bodies and destroy them too
                    for body in self.game.world.world.GetBodyList():
                        self.game.world.world.DestroyBody(body)

                    # Add ground, because we destroyed it before
                    self.game.world.add.ground()
                    # Also clear the points recorded in pens.
                    self.game.full_pos_list = \
                        [[] for _ in self.game.full_pos_list]
                elif event.action == 'focus_in':
                    self.game.in_focus = True
                elif event.action == 'focus_out':
                    self.game.in_focus = False
                elif event.action in self.game.toolList:
                    self.game.setTool(event.action)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.game.canvas.grab_focus()
            handled = False
        else:
            handled = False
        if handled:
            return handled
        else:
            return self.handleToolEvent(event)

    def handleToolEvent(self, event):
        # Overload to handle events for Tool subclasses
        pass

    def draw(self):
        # Default drawing method is draw the pen points.
        surface = self.game.world.renderer.get_surface()
        for key, info in self.game.trackinfo.iteritems():
            color = info[2]
            trackdex = info[4]
            try:
                pos_list = self.game.full_pos_list[trackdex]
                for i in range(0, len(pos_list), 2):
                    posx = int(pos_list[i])
                    posy = int(pos_list[i+1])
                    pygame.draw.circle(surface, color, (posx, posy), 2)
            except IndexError:
                pass

    def cancel(self):
        # Default cancel doesn't do anything
        pass

    def add_badge(self, message,
                  icon='trophy-icon-physics', from_='Physics'):
        badge = {
            'icon': icon,
            'from': from_,
            'message': message
        }
        icon_path = os.path.join(activity.get_bundle_path(),
                                 'icons',
                                 (icon+'.svg'))
        sugar_icons = os.path.join(
            os.path.expanduser('~'),
            '.icons')
        copy(icon_path, sugar_icons)

        if 'comments' in self.game.activity.metadata:
            comments = json.loads(self.game.activity.metadata['comments'])
            comments.append(badge)
            self.game.activity.metadata['comments'] = json.dumps(comments)
        else:
            self.game.activity.metadata['comments'] = json.dumps([badge])


# The circle creation tool
class CircleTool(Tool):
    name = 'Circle'
    icon = 'circle'
    toolTip = _('Circle')
    toolAccelerator = _('<ctrl>c')

    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = PALETTE_ICON_OBJECT_SETTINGS
    palette_data = PALETTE_OBJECT_DATA

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.radius = 40

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.game.world.add.ball(
                    self.pt1, self.radius,
                    dynamic=True, density=self.palette_data['density'],
                    restitution=self.palette_data['restitution'],
                    friction=self.palette_data['friction'])
                self.pt1 = None

    def draw(self):
        Tool.draw(self)
        # Draw a circle from pt1 to mouse
        if self.pt1 is not None:
            delta = distance(self.pt1,
                             tuple_to_int(pygame.mouse.get_pos()))
            if delta > 0:
                self.radius = max(delta, 5)
                pygame.draw.circle(self.game.screen, (100, 180, 255),
                                   self.pt1, int(self.radius), 3)
                pygame.draw.line(self.game.screen, (100, 180, 255), self.pt1,
                                 tuple_to_int(pygame.mouse.get_pos()), 1)

    def cancel(self):
        self.pt1 = None


# The box creation tool
class BoxTool(Tool):
    name = 'Box'
    icon = 'box'
    toolTip = _('Box')
    toolAccelerator = _('<ctrl>b')

    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = PALETTE_ICON_OBJECT_SETTINGS
    palette_data = PALETTE_OBJECT_DATA

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.rect = None
        self.width = 80
        self.height = 80

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and self.pt1 is not None:
                mouse_x_y = tuple_to_int(event.pos)
                if mouse_x_y[0] == self.pt1[0] and mouse_x_y[1] == self.pt1[1]:
                    self.rect = pygame.Rect(self.pt1,
                                            (-self.width, -self.height))
                    self.rect.normalize()
                self.game.world.add.rect(
                    self.rect.center,
                    max(self.rect.width, 10) / 2,
                    max(self.rect.height, 10) / 2,
                    dynamic=True,
                    density=self.palette_data['density'],
                    restitution=self.palette_data['restitution'],
                    friction=self.palette_data['friction'])
                self.pt1 = None

    def draw(self):
        Tool.draw(self)
        # Draw a box from pt1 to mouse
        if self.pt1 is not None:
            mouse_x_y = tuple_to_int(pygame.mouse.get_pos())
            if mouse_x_y[0] != self.pt1[0] or mouse_x_y[1] != self.pt1[1]:
                self.width = mouse_x_y[0] - self.pt1[0]
                self.height = mouse_x_y[1] - self.pt1[1]
                self.rect = pygame.Rect(self.pt1, (self.width, self.height))
                self.rect.normalize()
                pygame.draw.rect(self.game.screen, (100, 180, 255),
                                 self.rect, 3)

    def cancel(self):
        self.pt1 = None
        self.rect = None


# The triangle creation tool
class TriangleTool(Tool):
    name = 'Triangle'
    icon = 'triangle'
    toolTip = _('Triangle')
    toolAccelerator = _('<ctrl>t')

    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = PALETTE_ICON_OBJECT_SETTINGS
    palette_data = PALETTE_OBJECT_DATA

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.pt1 = None
        self.vertices = None
        self.line_delta = [0, -80]

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pt1 = tuple_to_int(event.pos)
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1 and self.pt1 is not None:
                mouse_x_y = tuple_to_int(event.pos)
                if mouse_x_y[0] == self.pt1[0] and mouse_x_y[1] == self.pt1[1]:
                    self.pt1 = [mouse_x_y[0] - self.line_delta[0],
                                mouse_x_y[1] - self.line_delta[1]]
                    self.vertices = constructTriangleFromLine(self.pt1,
                                                              mouse_x_y)

                # Use minimum sized triangle if user input too small
                minimum_size_check = float(distance(self.pt1, mouse_x_y))
                if minimum_size_check < 20:
                    middle_x = (self.pt1[0] + mouse_x_y[0]) / 2.0
                    self.pt1[0] = middle_x - (((middle_x - self.pt1[0]) /
                                              minimum_size_check) * 20)
                    mouse_x_y[0] = middle_x - (((middle_x - mouse_x_y[0]) /
                                               minimum_size_check) * 20)
                    middle_y = (self.pt1[1] + mouse_x_y[1]) / 2.0
                    self.pt1[1] = middle_y - (((middle_y - self.pt1[1]) /
                                              minimum_size_check) * 20)
                    mouse_x_y[1] = middle_y - (((middle_y - mouse_x_y[1]) /
                                               minimum_size_check) * 20)
                    self.vertices = constructTriangleFromLine(self.pt1,
                                                              mouse_x_y)

                self.game.world.add.convexPoly(
                    self.vertices,
                    dynamic=True,
                    density=self.palette_data['density'],
                    restitution=self.palette_data['restitution'],
                    friction=self.palette_data['friction'])
                self.pt1 = None
                self.vertices = None

    def draw(self):
        Tool.draw(self)
        # Draw a triangle from pt1 to mouse
        if self.pt1 is not None:
            mouse_x_y = tuple_to_int(pygame.mouse.get_pos())
            if mouse_x_y[0] != self.pt1[0] or mouse_x_y[1] != self.pt1[1]:
                self.vertices = constructTriangleFromLine(self.pt1, mouse_x_y)
                self.line_delta = [mouse_x_y[0] - self.pt1[0],
                                   mouse_x_y[1] - self.pt1[1]]
                pygame.draw.polygon(self.game.screen, (100, 180, 255),
                                    self.vertices, 3)
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.pt1, mouse_x_y, 1)

    def cancel(self):
        self.pt1 = None
        self.vertices = None


# The Polygon creation tool
class PolygonTool(Tool):
    name = 'Polygon'
    icon = 'polygon'
    toolTip = _('Polygon')
    toolAccelerator = _('<ctrl>p')

    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = PALETTE_ICON_OBJECT_SETTINGS
    palette_data = PALETTE_OBJECT_DATA

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None
        self.previous_vertices = None
        self.safe = False

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if hasattr(event, 'button') and event.button == 1:
            if event.type == MOUSEBUTTONDOWN and self.vertices is None:
                self.vertices = [tuple_to_int(event.pos)]
                self.safe = False
            if event.type == MOUSEBUTTONUP and self.vertices is not None and \
                    len(self.vertices) == 1 and \
                    tuple_to_int(event.pos)[0] == self.vertices[0][0] and \
                    tuple_to_int(event.pos)[1] == self.vertices[0][1]:
                if self.previous_vertices is not None:
                    last_x_y = self.previous_vertices[-1]
                    delta_x = last_x_y[0] - tuple_to_int(event.pos)[0]
                    delta_y = last_x_y[1] - tuple_to_int(event.pos)[1]
                    self.vertices = [[i[0] - delta_x, i[1] - delta_y]
                                     for i in self.previous_vertices]
                    self.safe = True
                    self.game.world.add.complexPoly(
                        self.vertices,
                        dynamic=True,
                        density=self.palette_data['density'],
                        restitution=self.palette_data['restitution'],
                        friction=self.palette_data['friction'])
                self.vertices = None
            elif (event.type == MOUSEBUTTONUP or
                  event.type == MOUSEBUTTONDOWN):
                if self.vertices is None or (tuple_to_int(event.pos)[0]
                                             == self.vertices[-1][0] and
                                             tuple_to_int(event.pos)[1]
                                             == self.vertices[-1][1]):
                    # Skip if coordinate is same as last one
                    return
                if distance(tuple_to_int(event.pos), self.vertices[0]) < 15 \
                        and self.safe:
                    self.vertices.append(self.vertices[0])  # Connect polygon
                    self.game.world.add.complexPoly(
                        self.vertices,
                        dynamic=True,
                        density=self.palette_data['density'],
                        restitution=self.palette_data['restitution'],
                        friction=self.palette_data['friction'])
                    self.previous_vertices = self.vertices[:]
                    self.vertices = None
                elif distance(tuple_to_int(event.pos), self.vertices[0]) < 15:
                    self.vertices = None
                else:
                    self.vertices.append(tuple_to_int(event.pos))
                    if distance(tuple_to_int(event.pos),
                                self.vertices[0]) > 54:
                        self.safe = True

    def draw(self):
        Tool.draw(self)
        # Draw the poly being created
        if self.vertices:
            for i in range(len(self.vertices) - 1):
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.vertices[i], self.vertices[i + 1], 3)
            pygame.draw.line(self.game.screen, (100, 180, 255),
                             self.vertices[-1],
                             tuple_to_int(pygame.mouse.get_pos()), 3)
            pygame.draw.circle(self.game.screen, (100, 180, 255),
                               self.vertices[0], 15, 3)

    def cancel(self):
        self.vertices = None


# The magic pen tool
class MagicPenTool(Tool):
    name = 'Magicpen'
    icon = 'magicpen'
    toolTip = _('Draw')
    toolAccelerator = _('<ctrl>d')

    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = PALETTE_ICON_OBJECT_SETTINGS
    palette_data = PALETTE_OBJECT_DATA

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None
        self.previous_vertices = None
        self.safe = False

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.vertices = [tuple_to_int(event.pos)]
            self.safe = False
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if len(self.vertices) == 1 and self.previous_vertices is not None:
                last_x_y = self.previous_vertices[-1]
                delta_x = last_x_y[0] - tuple_to_int(event.pos)[0]
                delta_y = last_x_y[1] - tuple_to_int(event.pos)[1]
                self.vertices = [[i[0] - delta_x, i[1] - delta_y]
                                 for i in self.previous_vertices]
                self.safe = True
            if self.vertices and self.safe:
                self.game.world.add.complexPoly(
                    self.vertices, dynamic=True,
                    density=self.palette_data['density'],
                    restitution=self.palette_data['restitution'],
                    friction=self.palette_data['friction'])
                self.previous_vertices = self.vertices[:]
            self.vertices = None
        elif event.type == MOUSEMOTION and self.vertices:
            self.vertices.append(tuple_to_int(event.pos))
            if distance(tuple_to_int(event.pos), self.vertices[0]) >= 55 and \
                    len(self.vertices) > 3:
                self.safe = True

    def draw(self):
        Tool.draw(self)
        # Draw the poly being created
        if self.vertices:
            if len(self.vertices) > 1:
                for i in range(len(self.vertices) - 1):
                    pygame.draw.line(self.game.screen, (100, 180, 255),
                                     self.vertices[i], self.vertices[i + 1], 3)
                pygame.draw.line(self.game.screen, (100, 180, 255),
                                 self.vertices[-1],
                                 tuple_to_int(pygame.mouse.get_pos()), 3)
                pygame.draw.circle(self.game.screen, (100, 180, 255),
                                   self.vertices[0], 15, 3)

    def cancel(self):
        self.vertices = None


# The grab tool
class GrabTool(Tool):
    name = 'Grab'
    icon = 'grab'
    toolTip = _('Grab')
    toolAccelerator = _('<ctrl>g')

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self._current_body = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        # We handle two types of 'grab' depending on simulation running or not
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Grab the first object at the mouse pointer
                bodylist = self.game.world.get_bodies_at_pos(
                    tuple_to_int(event.pos),
                    include_static=False)
                if bodylist and len(bodylist) > 0:
                    if self.game.world.run_physics:
                        self.game.world.add.mouseJoint(bodylist[0],
                                                       tuple_to_int(event.pos))
                    else:
                        self._current_body = bodylist[0]
        elif event.type == MOUSEBUTTONUP:
            # Let it go
            if event.button == 1:
                if self.game.world.run_physics:
                    self.game.world.add.remove_mouseJoint()
                else:
                    self._current_body = None
        elif event.type == MOUSEMOTION and event.buttons[0]:
            # Move it around
            if self.game.world.run_physics:
                # Use box2D mouse motion
                self.game.world.mouse_move(tuple_to_int(event.pos))
            else:
                # Position directly (if we have a current body)
                if self._current_body is not None:
                    x, y = self.game.world.to_world(tuple_to_int(event.pos))
                    x /= self.game.world.ppm
                    y /= self.game.world.ppm
                    self._current_body.position = (x, y)

    def cancel(self):
        self.game.world.add.remove_mouseJoint()


# The joint tool
class JointTool(Tool):
    name = 'Joint'
    icon = 'joint'
    toolTip = _('Joint')
    toolAccelerator = '<ctrl>j'

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button >= 1:
                # Grab the first body
                self.jb1pos = tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(
                    tuple_to_int(event.pos))
                self.jb2 = self.jb2pos = None
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                # Grab the second body
                self.jb2pos = tuple_to_int(event.pos)
                self.jb2 = self.game.world.get_bodies_at_pos(
                    tuple_to_int(event.pos))
                # If we have two distinct bodies, add a distance joint!
                if self.jb1 and self.jb2 and str(self.jb1) != str(self.jb2):
                    self.game.world.add.joint(self.jb1[0], self.jb2[0],
                                              self.jb1pos, self.jb2pos)
                #add joint to ground body
                #elif self.jb1:
                #    groundBody = self.game.world.world.GetGroundBody()
                #    self.game.world.add.joint(self.jb1[0], groundBody,
                #                              self.jb1pos, self.jb2pos)
                # regardless, clean everything up
                self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None

    def draw(self):
        Tool.draw(self)
        if self.jb1:
            pygame.draw.line(self.game.screen, (100, 180, 255), self.jb1pos,
                             tuple_to_int(pygame.mouse.get_pos()), 3)

    def cancel(self):
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None


# The pin tool
class PinTool(Tool):
    name = 'Pin'
    icon = 'pin'
    toolTip = _('Pin')
    toolAccelerator = _('<ctrl>o')

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            self.jb1pos = tuple_to_int(event.pos)
            self.jb1 = self.game.world.get_bodies_at_pos(
                tuple_to_int(event.pos))
            if self.jb1:
                self.game.world.add.joint(self.jb1[0], self.jb1pos)
            self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


# The motor tool
class MotorTool(Tool):
    name = 'Motor'
    icon = 'motor'
    toolTip = _('Motor')
    toolAccelerator = _('<ctrl>m')
    # Palette settings
    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = [
        {
            'name': 'speed',
            'icon_count': 4,
            'icons': ['motor-rabbit', 'motor-turtle',  'motor-turtle-2',
                      'motor-rabbit-2'],
            'icon_values': [100, 20, -20, -100],
            'active': 'motor-rabbit'
        },
    ]
    # Default value
    palette_data = {
        'speed': 100,
    }

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button >= 1:
                # Grab the first body
                self.jb1pos = tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(
                    tuple_to_int(event.pos))
                if self.jb1:
                    self.game.world.add.motor(
                        self.jb1[0], self.jb1pos,
                        speed=self.palette_data['speed'])
                self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


class RollTool(Tool):
    name = 'Roll'
    icon = 'roll'
    toolTip = _('Roll')
    toolAccelerator = _('<ctrl>r')

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.jb1 = self.jb1pos = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.jb1pos = tuple_to_int(event.pos)
                self.jb1 = self.game.world.get_bodies_at_pos(self.jb1pos)
                if self.jb1 and isinstance(self.jb1[0].userData, dict):
                    self.jb1[0].userData['rollMotor'] = {}
                    self.jb1[0].userData['rollMotor']['targetVelocity'] = -10
                    self.jb1[0].userData['rollMotor']['strength'] = 40
                self.jb1 = self.jb1pos = None

    def cancel(self):
        self.jb1 = self.jb1pos = None


# The destroy tool
class DestroyTool(Tool):
    name = 'Destroy'
    icon = 'destroy'
    toolTip = _('Erase')
    toolAccelerator = _('<ctrl>e')

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self.vertices = None

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)
        if pygame.mouse.get_pressed()[0]:
            if not self.vertices:
                self.vertices = []
            self.vertices.append(tuple_to_int(event.pos))
            if len(self.vertices) > 10:
                self.vertices.pop(0)

            tokill = self.game.world.get_bodies_at_pos(tuple_to_int(event.pos))

            if tokill:
                tracklist = self.game.trackinfo.items()
                destroyed_body = False
                for key, info in tracklist:
                    trackdex = info[4]
                    if 'track_indices' in tokill[0].userData and \
                       trackdex in tokill[0].userData['track_indices'] and \
                       info[3] is False:
                        self.game.world.world.DestroyBody(info[1])
                        self.game.trackinfo[key][3] = True
                        destroyed_body = True
                        break

                jointnode = tokill[0].GetJointList()
                if jointnode and not destroyed_body:
                    joint = jointnode.joint
                    self.game.world.world.DestroyJoint(joint)
                elif not destroyed_body:
                    self.game.world.world.DestroyBody(tokill[0])
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.cancel()

    def draw(self):
        Tool.draw(self)
        # Draw the trail
        if self.vertices:
            if len(self.vertices) > 1:
                pygame.draw.lines(self.game.screen, (255, 0, 0), False,
                                  self.vertices, 3)

    def cancel(self):
        self.vertices = None


# Track tool
class TrackTool(Tool):
    name = 'Track'
    icon = 'track'
    toolTip = _('Track Object')
    toolAccelerator = _('<ctrl>r')

    def __init__(self, game):
        Tool.__init__(self, game)
        self.radius = 1
        self.added_badge = False

    def handleToolEvent(self, event):
        Tool.handleToolEvent(self, event)

        if pygame.mouse.get_pressed()[0]:
            current_body = self.game.world.get_bodies_at_pos(
                tuple_to_int(event.pos))
            if current_body:
                current_body = current_body[0]
                color = current_body.userData['color']
                point_pos = tuple_to_int(event.pos)
                track_circle = self.game.world.add.ball(
                    point_pos, self.radius, dynamic=True, density=0.001,
                    restitution=0.16, friction=0.1)
                trackdex = self.game.tracked_bodies
                track_circle.userData['track_index'] = trackdex
                dictkey = 'pen{0}'.format(trackdex)
                self.game.world.add.joint(
                    track_circle, current_body, point_pos, point_pos, False)

                if 'track_indices' in current_body.userData:
                    current_body.userData['track_indices'].append(trackdex)
                else:
                    current_body.userData['track_indices'] = [trackdex]

                self.game.trackinfo[dictkey] = [0, 1, 2, 4, 5]
                self.game.trackinfo[dictkey][0] = current_body
                self.game.trackinfo[dictkey][1] = track_circle
                self.game.trackinfo[dictkey][2] = color
                self.game.trackinfo[dictkey][3] = False  # Pen destroyed or not
                self.game.trackinfo[dictkey][4] = trackdex  # Tracking index.
                self.game.tracked_bodies += 1  # counter of tracked bodies

                if not self.added_badge:
                    self.add_badge(message='Congratulations! You just added a'
                                           ' Pen to your machine!',
                                   from_='Isacc Newton')
                    self.added_badge = True


class ChainTool(Tool):
    name = 'Chain'
    icon = 'chain'
    toolTip = _('Chain')
    toolAccelerator = '<ctrl>i'

    # Palette settings
    palette_enabled = True
    palette_mode = PALETTE_MODE_ICONS
    palette_settings = [
        {
            'name': 'chain',
            'icon_count': 3,
            'icons': ['chain-fine', 'chain-medium', 'chain-coarse'],
            'icon_values': [0, 1, 2],
            'active': 'chain-medium'
        }
    ]
    palette_data = [
        {
            'link_length': 10,
            'radius': 3
        },
        {
            'link_length': 20,
            'radius': 6
        },
        {
            'link_length': 40,
            'radius': 12
        },
    ]
    palette_data_type = 1

    def __init__(self, gameInstance):
        Tool.__init__(self, gameInstance)
        self._clear()

    def handleToolEvent(self, event):
        radius = int(self.palette_data[self.palette_data_type]['radius'])
        Tool.handleToolEvent(self, event)
        if event.type == MOUSEBUTTONDOWN:
            self._body_1 = self._body_2 = self._pos_1 = self._pos_2 = None
            if event.button >= 1:
                # Find body 1
                self._pos_1 = tuple_to_int(event.pos)
                self._body_1 = self._find_body(event.pos)
                if self._body_1 is None:
                    self._clear()
                    return
        elif event.type == MOUSEBUTTONUP:
            if self._body_1 is None or self._body_1 == []:
                return
            if event.button == 1:
                # Find body 2 (or create a circle object)
                self._pos_2 = tuple_to_int(event.pos)
                self._body_2 = self._find_body(event.pos)
                if self._body_2 is None:
                    self._body_2 = self.game.world.add.ball(
                        self._pos_2, radius, dynamic=True, density=1.0,
                        restitution=0.16, friction=0.1)
                    self._body_2.userData['color'] = (0, 0, 0)
                '''
                # Don't make a chain from a body to itself
                if str(self._body_1) == str(self._body_2):
                    self._clear()
                    return
                '''
                self.make_chain()

    def draw(self):
        Tool.draw(self)
        if self._body_1:
            pygame.draw.line(self.game.screen, (100, 180, 255), self._pos_1,
                             tuple_to_int(pygame.mouse.get_pos()), 3)

    def _clear(self):
        self._body_1 = self._body_2 = self._pos_1 = self._pos_2 = None

    def cancel(self):
        self._clear()

    def make_chain(self):
        dist = int(distance(self._pos_1, self._pos_2) + 0.5)
        x1, y1 = self._pos_1
        x2, y2 = self._pos_2
        bearing = math.atan2((y2 - y1), (x2 - x1))
        link_length = self.palette_data[self.palette_data_type]['link_length']
        radius = int(self.palette_data[self.palette_data_type]['radius'])

        if dist < link_length:  # Too short to make a chain
            self.game.world.add.joint(
                self._body_1, self._body_2, self._pos_1, self._pos_2)
            self._clear()
            return

        # Draw circles along the path and join them together
        prev_circle = self._body_1
        prev_pos = tuple_to_int((x1, y1))
        for current_point in range(int(link_length / 2.), dist,
                                   int(link_length)):
            x = x1 + (current_point) * math.cos(bearing)
            y = y1 + (current_point) * math.sin(bearing)
            circle = self.game.world.add.ball(tuple_to_int((x, y)),
                                              radius, dynamic=True,
                                              density=1.0,
                                              restitution=0.16, friction=0.1)
            circle.userData['color'] = (0, 0, 0)
            self.game.world.add.joint(
                prev_circle, circle, prev_pos, tuple_to_int((x, y)),
                False)
            if (current_point + link_length) >= dist:
                self.game.world.add.joint(
                    circle, self._body_2, tuple_to_int((x, y)),
                    self._pos_2, False)
            prev_circle = circle
            prev_pos = tuple_to_int((x, y))

        self._clear()

    def _find_body(self, pos):
        body = self.game.world.get_bodies_at_pos(tuple_to_int(pos))
        if isinstance(body, list) and len(body) > 0:
            return body[0]
        else:
            return None


def getAllTools():
    return [MagicPenTool,
            CircleTool,
            TriangleTool,
            BoxTool,
            PolygonTool,
            GrabTool,
            MotorTool,
            PinTool,
            JointTool,
            ChainTool,
            TrackTool,
            DestroyTool]

allTools = getAllTools()
