# Physics.activity
# Go eat an apple, Newton! 
# Alex's Branch!
# Brian Jordan
# Modified from Alex Levenson's testbed
# Modified from Elements demos

import pygame
from pygame.locals import *
from pygame.color import *

import elements
from elements import Elements

def main():
    # set up pygame
    pygame.init()
    size = (1200,900) # A - Any way of getting a lower resolution? Changing size?
    #size = (1024, 768)
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
        
    # set up the world
    world = elements.Elements((400,400)) # A - here?
    world.renderer.set_surface(screen)

    # set up enviornment
    world.add.ground()
    #world.add.wall((100, 100), (300, 300), 5)
    #body=world.add.rect((900,300),width=300,height=25)    
    #world.add.joint(body)

    # loop control
    go = True
    
    a = 0
    jb1=jb2=jb1pos=jb2pos=None
    
    # Main Loop: - processes key and mouse events, world update and draw
    while go:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                # Quit the application -- bye bye!
                go = False
                
            elif event.type == KEYDOWN and event.key == K_SPACE:
                # Pause with SPACE
                world.run_physics = not world.run_physics
	   
            # Adds Mouse-->Object joints for grabbing/throwing objects
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Add Mouse-->Object Joint if at an Object
                bodylist = world.get_bodies_at_pos(event.pos, include_static=False)
                if bodylist and len(bodylist) > 0:
                    world.add.mouseJoint(bodylist[0], event.pos) 
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                # Delete Mouse-->Object Joint
                world.add.remove_mouseJoint()

            # Uses Box2D mouse movement 
            elif event.type == MOUSEMOTION and event.buttons[0]:
                world.mouse_move(event.pos)
            
            # Adds Object-->Object joints for connecting objects
            elif event.type == MOUSEBUTTONDOWN and event.button == 3:
                # Connect bodies
                jb1pos = event.pos
                jb1 = world.get_bodies_at_pos(event.pos)
                jb2 = None
                jb2pos = None
            elif event.type == MOUSEBUTTONUP and event.button == 3:
                jb2 = world.get_bodies_at_pos(event.pos)
                jb2pos = event.pos
                if jb1 and jb2 and str(jb1) != str(jb2):
                    world.add.joint(jb1[0],jb2[0],jb1pos,jb2pos)
                jb1 = jb2 = jb1pos = jb2pos = None

            elif event.type == KEYDOWN:
                if event.key == K_1:
                    #add a triangle
                    x,y = pygame.mouse.get_pos()
                    world.add.triangle((0,0),sidelength=40)
                    world.add.ball((x,y), radius=20)
                elif event.key == K_2:
                    #add a circle
                    x,y = pygame.mouse.get_pos()
                    world.add.ball((100,0),radius=20)
                    #world.add.rect((100,0),width=40,height=20,angle=90)
                    #a+=10
                elif event.key == K_3:
                    x,y = pygame.mouse.get_pos()
                    world.add.ball((200,0),radius=20)
                elif event.key == K_4:
	        		x,y = pygame.mouse.get_pos()
	        		world.add.ball((300,0),radius=30)
                elif event.key == K_5:
	                x,y = pygame.mouse.get_pos()
	                world.add.ball((400,0),radius=40)
                elif event.key == K_6:
	                x,y = pygame.mouse.get_pos()
	                world.add.ball((500,0),radius=50)

                elif event.key == K_7:
                    x,y = pygame.mouse.get_pos()
                    world.add.ball((x,y),radius=60)
                #elif event.key == K_8:
                #    x,y = pygame.mouse.get_pos()
                #    world.add.ball((x,y),radius=20)

                elif event.key == K_9:
                    # Add many triangles
                    x, y = pygame.mouse.get_pos()
                    for i in range(5):
                        for j in range(5):
                            world.add.triangle((x-i,y-j), sidelength=20)
                            #a+=10 # Rotate 10 degs
		
                elif event.key == K_8:
                    #add many boxes
                    x,y = pygame.mouse.get_pos()
                    #for i in range(5):
                    #    for j in range(5): 
                    i = 0
                    for j in range(20):
                        world.add.rect((x-i,y-(j*500)),width=20,height=10,angle=a)
                        #world.add.ball((x,y-(j*500)),radius=60) 
                         #a+=10            
        # Clear Display
        screen.fill((255,255,255))

        # Update & Draw World
        world.update()
        world.draw()

        if jb1pos:
            pygame.draw.line(screen,THECOLORS["red"],jb1pos,pygame.mouse.get_pos(),3)

#        pygame.draw.aaline(screen,THECOLORS["red"],(0,0),(1200,900),20)


        # Flip Display
        pygame.display.flip()
        
        # Try to stay at 30 FPS
        clock.tick(30) # originally 50
        x,y = pygame.mouse.get_pos()
        

        # output framerate in caption
        pygame.display.set_caption("x: %i | y: %i | elements: %i | fps: %i" % (x, y, world.element_count, int(clock.get_fps())))
if __name__ == "__main__":
    main()
