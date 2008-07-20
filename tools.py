#==================================================================
#                           Physics.activity
#                              Tool Classes
#                           By Alex Levenson
#==================================================================
import pygame
from pygame.locals import *
from helpers import *
from inspect import getmro
# tools that can be used superlcass
class Tool(object):
    name = "Tool"
    icon = "icon"
    toolTip = "Tool Tip"
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Tool"
    def handleEvents(self,event):
        handled = True
        # default event handling
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            # bye bye! Hope you had fun!
            self.game.running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                #space pauses
                self.game.world.run_physics = not self.game.world.run_physics  
            elif event.key == K_t:
                self.game.setTool("triangle")
            elif event.key == K_b:
                self.game.setTool("box")
            elif event.key == K_c:
                self.game.setTool("circle")
            elif event.key == K_j:
                self.game.setTool("joint")
            elif event.key == K_p:
                self.game.setTool("polygon")
            elif event.key == K_g:
                self.game.setTool("grab")
            elif event.key == K_d:
                self.game.setTool("destroy")
            elif event.key == K_m:
                self.game.setTool("magicpen")
            #elif event.key == K_g:
            #    self.game.setTool("gear")
            # Game/joystick-related keys
            elif event.key == K_KP4: # Left gamepad, left arrow
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(9000) 
                elif self.game.debug: print "Left gamepad left arrow error: no joystick object selected"
            elif event.key == K_KP6: # Left gamepad, right arrow
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(9000) 
                elif self.game.debug: print "Left gamepad right arrow error: no joystick object selected"
            elif event.key == K_KP8: # Left gamepad, up arrow
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(9000) 
                elif self.game.debug: print "Left gamepad up arrow error: no joystick object selected"
            elif event.key == K_KP2: # Left gamepad, down arrow
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(9000) 
                elif self.game.debug: print "Left gamepad down arrow error: no joystick object selected"
            elif event.key == K_KP7: # Right gamepad, square
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(-9000) 
                elif self.game.debug: print "Right gamepad square button error: no joystick object selected"
            elif event.key == K_KP1: # Right gamepad, check
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(-9000) 
                elif self.game.debug: print "Right gamepad check button error: no joystick object selected"
            elif event.key == K_KP9: # Right gamepad, circle
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(-9000) 
                elif self.game.debug: print "Right gamepad circle button error: no joystick object selected"
            elif event.key == K_KP3: # Right gamepad, X
                if self.game.joystickobject:
                    self.game.joystickobject[0].ApplyTorque(-9000) 
                elif self.game.debug: print "Right gamepad X button error: no joystick object selected"
        elif event.type == USEREVENT:
            if hasattr(event,"action"):
                if self.game.toolList.has_key(event.action): self.game.setTool(event.action)
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            self.game.canvas.grab_focus()
            handled = False
        else:
            handled = False
        return handled                                     
    def draw(self):
        # default drawing method is don't draw anything
        pass
    def cancel(self):
        # default cancel doesn't do anything
        pass

# The circle creation tool        
class CircleTool(Tool): 
    name = "circle"
    icon = "circle"
    toolTip = "Circle"
   
    def __init__(self,gameInstance):
        self.game = gameInstance
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
                        self.game.world.add.ball(self.pt1,self.radius, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
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
            pygame.draw.circle(self.game.screen, (100,180,255),self.pt1,self.radius,thick) 
            pygame.draw.line(self.game.screen,(100,180,255),self.pt1,pygame.mouse.get_pos(),1)  
    def cancel(self):
        self.pt1 = None  
        self.radius = None
   
# The box creation tool        
class BoxTool(Tool):    
    name = "box"
    icon = "box"
    toolTip = "Box"

    def __init__(self,gameInstance):
        self.game = gameInstance
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
                        self.game.world.add.rect(self.rect.center, self.rect.width/2, self.rect.height/2, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                   
                    self.pt1 = None        
                                
    def draw(self):
        # draw a box from pt1 to mouse
        if self.pt1 != None:
            width = pygame.mouse.get_pos()[0] - self.pt1[0]
            height = pygame.mouse.get_pos()[1] - self.pt1[1]
            self.rect = pygame.Rect(self.pt1, (width, height))
            self.rect.normalize()           
            pygame.draw.rect(self.game.screen, (100,180,255),self.rect,3)   
    def cancel(self):
        self.pt1 = None  
        self.rect = None      
           
# The triangle creation tool        
class TriangleTool(Tool): 
    name = "triangle"
    icon = "triangle"
    toolTip = "Triangle"
   
    def __init__(self,gameInstance):
        self.game = gameInstance
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
                    if distance(self.pt1,pygame.mouse.get_pos()) > 15: # elements doesn't like tiny shapes :(
                        self.game.world.add.convexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                    self.pt1 = None
                    self.vertices = None                    
    def draw(self):
        # draw a triangle from pt1 to mouse
        if self.pt1 != None:
            self.vertices = constructTriangleFromLine(self.pt1,pygame.mouse.get_pos())
            pygame.draw.polygon(self.game.screen, (100,180,255),self.vertices, 3) 
            pygame.draw.line(self.game.screen,(100,180,255),self.pt1,pygame.mouse.get_pos(),1)  
    
    def cancel(self):
        self.pt1 = None        
        self.vertices = None

# The Polygon creation tool        
class PolygonTool(Tool):  
    name = "polygon"
    icon = "polygon"
    toolTip = "Polygon"
  
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Polygon"
        self.vertices = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(PolygonTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.vertices:
                        self.vertices=[event.pos]  
                    elif distance(event.pos,self.vertices[0]) < 15:                     
                        #self.vertices.append(self.vertices[0]) #connect the polygon
                        gons = decomposePoly(self.vertices)
                        for g in gons:
                            self.game.world.add.convexPoly(g, dynamic=True, density=1.0, restitution=0.16, friction=0.5)
                        #self.game.world.add.complexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                        self.vertices = None  
                    else:
                        self.vertices.append(event.pos)
                if event.button == 3:
                    if self.vertices:
                        self.vertices.append(event.pos)
                        self.game.world.add.complexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)
                        self.vertices = None
                                
    def draw(self):
        # draw the poly being created
        if self.vertices:
            for i in range(len(self.vertices)-1):
                pygame.draw.line(self.game.screen,(100,180,255),self.vertices[i],self.vertices[i+1],3)
            pygame.draw.line(self.game.screen,(100,180,255),self.vertices[-1],pygame.mouse.get_pos(),3)
            pygame.draw.circle(self.game.screen,(100,180,255),self.vertices[0],15,3)  
    
    def cancel(self):       
        self.vertices = None

# The magic pen tool        
class MagicPenTool(Tool):
    name = "magicpen"
    icon = "magicpen"
    toolTip = "Magic Pen"
    
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Magic Pen"
        self.vertices = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(MagicPenTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.vertices:
                        self.vertices=[event.pos]  
                    elif distance(event.pos,self.vertices[0]) < 15:                     
                        self.vertices.append(self.vertices[0]) #connect the polygon
                        self.game.world.add.complexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                        self.vertices = None  
                    else:
                        self.vertices.append(event.pos)
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                        if self.vertices:
                            self.game.world.add.complexPoly(self.vertices, dynamic=True, density=1.0, restitution=0.16, friction=0.5)                    
                        self.vertices = None
            elif event.type == MOUSEMOTION:
                if self.vertices:
                    self.vertices.append(event.pos)
                                
    def draw(self):
        # draw the poly being created
        if self.vertices:
            for i in range(len(self.vertices)-1):
                pygame.draw.line(self.game.screen,(100,180,255),self.vertices[i],self.vertices[i+1],3)
            pygame.draw.line(self.game.screen,(100,180,255),self.vertices[-1],pygame.mouse.get_pos(),3)
            pygame.draw.circle(self.game.screen,(100,180,255),self.vertices[0],15,3)  
    
    def cancel(self):       
        self.vertices = None

# The grab tool        
class GrabTool(Tool):
    name = "grab"
    icon = "grab"
    toolTip = "Grab"
    
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Grab"
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(GrabTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # grab the first object at the mouse pointer
                    bodylist = self.game.world.get_bodies_at_pos(event.pos, include_static=False) 
                    if bodylist and len(bodylist) > 0:
                        self.game.world.add.mouseJoint(bodylist[0], event.pos)               
            elif event.type == MOUSEBUTTONUP:
                # let it go
                if event.button == 1:
                    self.game.world.add.remove_mouseJoint()
            # use box2D mouse motion
            elif event.type == MOUSEMOTION and event.buttons[0]:
                self.game.world.mouse_move(event.pos)
            
    def cancel(self):
        self.game.world.add.remove_mouseJoint()                        
    
# The joint tool        
class JointTool(Tool):
    name = "joint"
    icon = "joint"
    toolTip = "Joint"
    
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Joint"
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(JointTool,self).handleEvents(event):
            if event.type == MOUSEBUTTONDOWN:
                if event.button >= 1:
                    # grab the first body
                    self.jb1pos = event.pos
                    self.jb1 = self.game.world.get_bodies_at_pos(event.pos)
                    self.jb2 = self.jb2pos = None
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    # grab the second body
                    self.jb2pos = event.pos
                    self.jb2 = self.game.world.get_bodies_at_pos(event.pos)
                    # if we have two distinct bodies, add a distance joint!
                    if self.jb1 and self.jb2 and str(self.jb1) != str(self.jb2):
                        self.game.world.add.distanceJoint(self.jb1[0],self.jb2[0],self.jb1pos,self.jb2pos)                    
                    # If there's only one body, add a fixed joint
                    elif self.jb2:
                        self.game.world.add.fixedJoint(self.jb2[0],self.jb2pos)
                    # regardless, clean everything up
                    self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None
                if event.button == 3:
                    # add a centered fixed joint
                    '''self.jb2 = self.game.world.get_bodies_at_pos(event.pos)
                    if self.jb2:
                        self.game.world.add.fixedJoint(self.jb2[0])
                    # regardless, clean everything up
                    self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None'''
                    if self.jb1:
                        self.game.world.add.motor(self.jb1[0],self.jb1pos)
                    self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None
    def draw(self):
        if self.jb1:
            pygame.draw.line(self.game.screen,(100,180,255),self.jb1pos,pygame.mouse.get_pos(),3)
    
    def cancel(self):
        self.jb1 = self.jb2 = self.jb1pos = self.jb2pos = None             
        
# The destroy tool        
class DestroyTool(Tool):
    name = "destroy"
    icon = "destroy"
    toolTip = "Destroy"
    
    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Destroy"
        self.vertices = None
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        if not super(DestroyTool,self).handleEvents(event):
            if pygame.mouse.get_pressed()[0]:
                if not self.vertices: self.vertices = []
                self.vertices.append(pygame.mouse.get_pos())
                if len(self.vertices) > 10:
                    self.vertices.pop(0)
                tokill = self.game.world.get_bodies_at_pos(pygame.mouse.get_pos())
                if tokill:                        
                        self.game.world.world.DestroyBody(tokill[0])
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                self.cancel()
    def draw(self):
        # draw the trail
        if self.vertices:
            if len(self.vertices) > 1:
                pygame.draw.lines(self.game.screen,(255,0,0),False,self.vertices,3)

    def cancel(self):
        self.vertices = None     

 # The joystick tool        
class JoystickTool(Tool):
    name = "joystick"
    icon = "magicpen" # for now
    toolTip = "Joystick"

    def __init__(self,gameInstance):
        self.game = gameInstance
        self.name = "Joystick"
        self.vertices = None
        #self.joystickobject
    def handleEvents(self,event):
        #look for default events, and if none are handled then try the custom events 
        super(JoystickTool,self).handleEvents(event)
        if pygame.mouse.get_pressed()[0]:
            if not self.vertices:
                self.vertices = []
                self.vertices.append(pygame.mouse.get_pos())
            if len(self.vertices) > 10:
                self.vertices.pop(0)
            self.game.joystickobject = self.game.world.get_bodies_at_pos(pygame.mouse.get_pos())
            if self.game.joystickobject:
                print "hi1"                
        #self.game.world.world.DestroyBody(self.joystickobject[0])
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self.cancel()
    def draw(self):
        # draw the trail
        if self.vertices:
            if len(self.vertices) > 1:
                pygame.draw.lines(self.game.screen,(255,0,0),False,self.vertices,3)

    def cancel(self):
        self.vertices = None


def getAllTools():
    this_mod = __import__(__name__)
    all = [val for val in this_mod.__dict__.values() if isinstance(val, type)]
    allTools = []
    for a in all:
        if getmro(a).__contains__(Tool) and a!= Tool: allTools.append(a)
    return allTools
            

allTools = getAllTools()
