#!/usr/bin/python
"""
This file is part of the 'Physics' Project
Physics is a 2D Physics Playground for Kids (supporting Box2D2)
Physics Copyright (C) 2008, Alex Levenson, Brian Jordan
Elements Copyright (C) 2008, The Elements Team, <elements@linuxuser.at>

Wiki:   http://wiki.laptop.org/wiki/Physics
IRC:    #olpc-physics on irc.freenode.org

Code:   http://dev.laptop.org/git?p=activities/physics
        git clone git://dev.laptop.org/activities/physics

License:  GPLv3 http://gplv3.fsf.org/
"""

import sys
import math
import pygame
from pygame.locals import *
from pygame.color import *
import olpcgames
sys.path.append("lib/")
import pkg_resources
sys.path.append("lib/Elements-0.12-py2.6.egg")
sys.path.append("lib/Elements-0.12-py2.5.egg")
sys.path.append("lib/Box2D-2.0.2b1-py2.5-linux-i686.egg")
import Box2D as box2d
import elements
import tools
from helpers import *


class PhysicsGame:
    def __init__(self,screen):
        self.screen = screen
        # get everything set up
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24) # font object
        self.canvas = olpcgames.ACTIVITY.canvas
        # create the name --> instance map for components
        self.toolList = {}
        for c in tools.allTools:
             self.toolList[c.name] = c(self)
        self.currentTool = self.toolList[tools.allTools[0].name]
        # set up the world (instance of Elements)
        self.box2d = box2d
        self.world = elements.Elements(self.screen.get_size())
        self.world.renderer.set_surface(self.screen)
        
        # set up static environment
        self.world.add.ground()    
        
    def run(self):
        self.running = True    
        while self.running:
            for event in pygame.event.get():
                self.currentTool.handleEvents(event)
            # Clear Display
            self.screen.fill((255,255,255)) #255 for white

            if self.world.run_physics:
                for body in self.world.world.GetBodyList():
                    if type(body.userData) == type({}):
                        if body.userData.has_key('rollMotor'):
                            diff =  body.userData['rollMotor']['targetVelocity']- body.GetAngularVelocity()
                            body.ApplyTorque(body.userData['rollMotor']['strength']*diff*body.getMassData().I)
        
            # Update & Draw World
            self.world.update()
            self.world.draw()
            
            # draw output from tools
            self.currentTool.draw()
                        
            # Flip Display
            pygame.display.flip()  
            
            # Try to stay at 30 FPS
            self.clock.tick(30) # originally 50    

    def setTool(self,tool):
        self.currentTool.cancel()
        self.currentTool = self.toolList[tool] 

def main():
    toolbarheight = 75
    tabheight = 45
    pygame.init()
    pygame.display.init()
    x,y  = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((x,y-toolbarheight-tabheight))
    # create an instance of the game
    game = PhysicsGame(screen) 
    # start the main loop
    game.run()

# make sure that main get's called
if __name__ == '__main__':
    main()

