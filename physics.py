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
            "triangle": TriangleTool(self),
            "box": BoxTool(self),
            "circle": CircleTool(self),
            "polygon": PolygonTool(self),
            "magicpen": MagicPenTool(self),
            "joint": JointTool(self),
            "grab": GrabTool(self),
            "destroy": DestroyTool(self)
        }
        self.currentTool = self.tools["Triangle"]
        
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
            
            #Print all the text on the screen
            text = self.font.render("Current Tool: "+self.currentTool.name, True, (255,255,255))
            textpos = text.get_rect(left=700,top=7)
            self.screen.blit(text,textpos)  
            
            # Flip Display
            pygame.display.flip()  
            
            # Try to stay at 30 FPS
            self.clock.tick(30) # originally 50    

    def setTool(self,tool):
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








