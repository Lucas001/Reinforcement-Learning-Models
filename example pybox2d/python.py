import time
from threading import Thread
from Box2D import *
from Box2D.b2 import *
import pygame, sys, math, random
from pygame.locals import *

running = True

colors = {
    staticBody  : (255,255,255,255),
    dynamicBody : (127,127,127,255),
}

def my_draw_polygon(polygon, body, fixture, height, winSurf):
    PPM=20.0 # pixels per meter
    vertices = [(body.transform*v)*PPM for v in polygon.vertices]
    vertices = [(v[0], height-v[1]) for v in vertices]
    pygame.draw.polygon(winSurf, colors[body.type], vertices)

class Draw(Thread):
    def __init__(self,outPygame,outEv,outBodyList):
        Thread.__init__(self)
        self.pygame_box2d_ratio=10.0
        self.pygame = outPygame
        self.ev = outEv

        self.car_x_size = 3
        self.car_y_size = 1

        self.screenX = 500
        self.screenY = 400
        self.windowSurface = self.pygame.display.set_mode((self.screenX, self.screenY))
        self.bodylist = outBodyList
        global my_draw_polygon
        polygonShape.draw = my_draw_polygon

    def loopDrawing(self):
        BLACK = (0, 0, 0)
        RED = (255, 0, 0)
        WHITE = (255,255,255)
        self.windowSurface.fill(BLACK)
     
        #self.pygame.draw.lines(self.windowSurface, RED, False, [(100,100), (150,200), (200,100)], 1)
        for body in self.bodylist:
            for fixture in body.fixtures:
                fixture.shape.draw(body, fixture, self.screenY,self.windowSurface)

        self.pygame.display.flip()

    def run(self):
        while self.ev.type != self.pygame.KEYDOWN:
            time.sleep(1.0/300.0)
            self.ev = self.pygame.event.poll()
            keys = self.pygame.key.get_pressed()
            self.loopDrawing()

        global running
        running = False
        return
            
class Physics(Thread):
    def __init__(self,outPygame, outEv, outBodyList):
        Thread.__init__(self)
        self.pygame_box2d_ratio=20.0
        self.world = b2World(gravity=(0,0), doSleep=True)
        self.timeStep = 1.0 / 300
        self.vel_iters = 3
        self.pos_iters = 1
        self.car_x_size = 3
        self.car_y_size = 1
        self.bodylist = outBodyList
        self.ev = outEv
        self.pygame = outPygame

    def create_dynamic_car(self,xpos,ypos,velocity):
        body= self.world.CreateDynamicBody(position=(xpos/self.pygame_box2d_ratio,ypos/self.pygame_box2d_ratio))
        box=body.CreatePolygonFixture(box=(self.car_x_size/2.0,self.car_y_size/2.0), density=1, friction=0.8)
        body.linearVelocity=(velocity,0)
        body.angularDamping=0.6
        return body

    def physicsLoop(self):
        if random.randint(1,1000)==2:
            self.bodylist.append(self.create_dynamic_car(0,random.randint(1,400),random.randint(1,10)))
            self.bodylist.append(self.create_dynamic_car(500,random.randint(1,400),-(random.randint(1,10))))

        self.world.Step(self.timeStep, self.vel_iters, self.pos_iters)
        self.world.ClearForces()

    def run(self):
        global running
        while running:
            self.ev = self.pygame.event.poll()
            keys = self.pygame.key.get_pressed()
            time.sleep(self.timeStep)
            self.physicsLoop()
        return

bodylist=[]
 
pygame.init()
pygame.display.set_caption('Box impacts')
ev = pygame.event.poll()

thread1 = Draw(pygame,ev,bodylist)
thread2 = Physics(pygame,ev, bodylist)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

pygame.quit()