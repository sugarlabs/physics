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
from sugar.activity import activity
import elements
from elements import Elements
from tools import *

# =======================================Classes==================================
# tools that can be used superlcass
class Tool(object):
    def __init__(self):
        # default tool name
        self.name = "Tool"
    def handleEvents(self,event):
        # default event handling
        global currentTool
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # bye bye! Hope you had fun!
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                #space pauses
                world.run_physics = not world.run_physics  
            elif event.key == K_c:
                currentTool.cancel()
                currentTool = tools["circle"]
            elif event.key == K_b:
                currentTool.cancel()
                currentTool = tools["box"]
            elif event.key == K_t: 
                currentTool.cancel()
                currentTool = tools["triangle"]
            elif event.key == K_j:
                currentTool.cancel()
                currentTool = tools["joint"]
            elif event.key == K_g:
                currentTool.cancel()
                currentTool = tools["grab"]
        else:
            # let the subclasses know that no events were handled yet
            return False  
        return True                                     
    def draw(self):
        # default drawing method is don't draw anything
        pass
    def cancel(self):
        # default cancel doesn't do anything
        pass

# The circle creation tool        
class CircleTool(Tool):    
    def __init__(self):
        self.name = "Circle"
        self.pt1 = None
        self.radius = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(CircleTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pt1 = pygame.mouse.get_pos()                    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:                    
                    if self.radius > 1: # elements doesn't like tiny shapes :(
                        world.add.ball(self.pt1,self.radius, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                    self.pt1 = None        
                    self.radius = None            
    def draw(self):
        # draw a circle from pt1 to mouse
        if self.pt1 != None:
            self.radius = distance(self.pt1,pygame.mouse.get_pos())
            if self.radius > 3: 
                thick = 3
            else:
                thick = 0
            pygame.draw.circle(screen, (100,180,255),self.pt1,self.radius,thick) 
            pygame.draw.line(screen,(100,180,255),self.pt1,pygame.mouse.get_pos(),3)  
    def cancel(self):
        self.pt1 = None  
        self.radius = None
   
# The box creation tool        
class BoxTool(Tool):    
    def __init__(self):
        self.name = "Box"
        self.pt1 = None        
        self.rect = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(BoxTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pt1 = pygame.mouse.get_pos()                    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.pt1!=None:                                 
                    if self.rect.width > 10 and self.rect.height > 10: # elements doesn't like small shapes :(
                        world.add.rect(self.rect.center, self.rect.width/2, self.rect.height/2, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                   
                    self.pt1 = None        
                                
    def draw(self):
        # draw a box from pt1 to mouse
        if self.pt1 != None:
            width = pygame.mouse.get_pos()[0] - self.pt1[0]
            height = pygame.mouse.get_pos()[1] - self.pt1[1]
            self.rect = pygame.Rect(self.pt1, (width, height))
            self.rect.normalize()           
            pygame.draw.rect(screen, (100,180,255),self.rect,3)   
    def cancel(self):
        self.pt1 = None  
        self.rect = None      
           
# The triangle creation tool        
class TriangleTool(Tool):    
    def __init__(self):
        self.name = "Triangle"
        self.pt1 = None
        self.vertices = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(TriangleTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.pt1 = pygame.mouse.get_pos()                    
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1 and self.pt1!= None:                    
                    if distance(self.pt1,pygame.mouse.get_pos()) > 10: # elements doesn't like tiny shapes :(
                        world.add.convexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                    self.pt1 = None
                    self.vertices = None                    
    def draw(self):
        # draw a triangle from pt1 to mouse
        if self.pt1 != None:
            self.vertices = constructTriangleFromLine(self.pt1,pygame.mouse.get_pos())
            pygame.draw.polygon(screen, (100,180,255),self.vertices, 3) 
            pygame.draw.line(screen,(100,180,255),self.pt1,pygame.mouse.get_pos(),3)  
    
    def cancel(self):
        self.pt1 = None        
        self.vertices = None

# The grab tool        
class GrabTool(Tool):    
    def __init__(self):
        self.name = "Grab"
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(GrabTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # grab the first object at the mouse pointer
                    bodylist = world.get_bodies_at_pos(event.pos, include_static=False) 
                    if bodylist and len(bodylist) > 0:
                        world.add.mouseJoint(bodylist[0], event.pos)               
            elif event.type == MOUSEBUTTONUP:
                # let it go
                if event.button == 1:
                    world.add.remove_mouseJoint()
            # use box2D mouse motion
            elif event.type == MOUSEMOTION and event.buttons[0]:
                world.mouse_move(event.pos)
    def cancel(self):
        world.add.remove_mouseJoint()                        
    


# set up pygame
pygame.init()
size = (700,700)
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24) # font object
    
# set up the world
world = elements.Elements(size)
world.renderer.set_surface(screen)

# load enviornment
world.add.ground()

# setup tools
tools = {
    "triangle": TriangleTool(),
    "box": BoxTool(),
    "circle": CircleTool(),
   # "joint": JointTool(),
    "grab": GrabTool()
}
currentTool = tools["triangle"]

# Main Loop:    
while True:
    for event in pygame.event.get():
        currentTool.handleEvents(event)
                        
    # Clear Display
    screen.fill((255,255,255))

    # Update & Draw World
    world.update()
    world.draw()
    
    # draw output from tools
    currentTool.draw()

    #Print all the text on the screen
    text = font.render("Current Tool: "+currentTool.name, True, (100,100,255))
    textpos = text.get_rect(left=1,top=1)  
    screen.blit(text,textpos)        

    # Flip Display
    pygame.display.flip()
    
    # Try to stay at 30 FPS
    clock.tick(30) # originally 50    