#==================================================================
#                           Physics.activity
#     An attempt at a Phun / Crayon Physics style physics game
#                  By Alex Levenson and Brian Jordan
#==================================================================

import sys
import math
import pygame
from pygame.locals import *
from pygame.color import *
import olpcgames
import elements
from elements import Elements
from elements.menu import *
from tools import *
from helpers import *

class PhysicsGame:
    def __init__(self,screen):
        self.screen = screen
        # get everything set up
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24) # font object
        
        # setup tools
        self.tools = {
            "Triangle": TriangleTool(self),
            "Box": BoxTool(self),
            "Circle": CircleTool(self),
            "Polygon": PolygonTool(self),
            "Magic Pen": MagicPenTool(self),
            "Joint": JointTool(self),
            "Grab": GrabTool(self),
            "Destroy": DestroyTool(self)
        }
        self.currentTool = self.tools["Triangle"]
        
        # setup the menus
        self.menu = MenuClass()  
        self.menu.set_width(self.screen.get_width()) 
        self.menu.addItem('Box', callback=self.setTool)
        self.menu.addItem('Circle', callback=self.setTool)
        self.menu.addItem('Triangle', callback=self.setTool)
        self.menu.addItem('Polygon', callback=self.setTool)
        self.menu.addItem('Magic Pen', callback=self.setTool)
        self.menu.addItem('Grab', callback=self.setTool)
        self.menu.addItem('Joint', callback=self.setTool)
        self.menu.addItem('Destroy', callback=self.setTool)
        
        # set up the world
        self.world = elements.Elements(self.screen.get_size())
        self.world.renderer.set_surface(self.screen)

        # load enviornment
        self.world.add.ground()    
    
    def run(self):
        self.running = True    
        while self.running:
            for event in pygame.event.get():
                self.currentTool.handleEvents(event)
            # Clear Display
            self.screen.fill((255,255,255))
        
            # Update & Draw World
            self.world.update()
            self.world.draw()
            
            # draw output from tools
            self.currentTool.draw()
            
            # draw the menu
            self.menu.draw(self.screen)
            
            #Print all the text on the screen
            text = self.font.render("Current Tool: "+self.currentTool.name, True, (255,255,255))
            textpos = text.get_rect(left=700,top=7)
            self.screen.blit(text,textpos)  
            
            # Flip Display
            pygame.display.flip()  
            
            # Try to stay at 30 FPS
            self.clock.tick(30) # originally 50    

    def setTool(self,tool,Discard=None):
        self.currentTool.cancel()
        self.currentTool = self.tools[tool]

def main():
    # compensate for the size of the toolbar
    toolbarheight = 75
    pygame.init()
    pygame.display.init()
    x,y  = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((x,y-toolbarheight))
    # create an instance of the game
    game = PhysicsGame(screen) 
    # start the main loop
    game.run()

# make sure that main get's called
if __name__ == '__main__':
    main()








