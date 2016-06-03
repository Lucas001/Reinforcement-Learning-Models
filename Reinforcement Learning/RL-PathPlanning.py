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
        for key,body in self.bodylist.items():
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

class ReinforcementLearning(object):
    def __init__(self):
        self.discount = 0.9
        self.rl_body_linVelocity = 0.0;
        self.rl_generation = 0

    def calculateStates(self, ):
        if(self.rl_generation == 0)

            
class Physics(Thread):
    def __init__(self,outPygame, outEv, outBodyList):
        Thread.__init__(self)
        self.pygame_box2d_ratio=20.0
        self.world = b2World(gravity=(0,-10), doSleep=True)
        self.timeStep = 1.0 / 300
        self.vel_iters = 3
        self.pos_iters = 1
        self.car_x_size = 3.5
        self.car_y_size = 0.5
        self.bodylist = outBodyList
        self.jointlist = []
        self.ev = outEv
        self.pygame = outPygame

        self.create_bodies()

    def __create_dynamic_car(self,xpos,ypos,velocity):
        body= self.world.CreateDynamicBody(position=(xpos/self.pygame_box2d_ratio,ypos/self.pygame_box2d_ratio))
        box=body.CreatePolygonFixture(box=(self.car_x_size/2.0,self.car_y_size/2.0), density=0.05, friction=10000)
        body.linearVelocity=(0,velocity)
        body.angularDamping=0.6
        return body

    def __create_joint(self, body1, body2, ptJoint):
        jointDef = b2RevoluteJointDef()
        jointDef.Initialize(body1, body2, ptJoint)
        jointDef.collideConnected = True
        jointDef.lowerAngle = 90
        jointDef.upperAngle = 90
        jointDef.enableLimit = False
        jointDef.maxMotorTorque = 5000
        jointDef.motorToque = 5000
        jointDef.motorSpeed = 0
        jointDef.enableMotor = True

        revoluteJoint = self.world.CreateJoint(jointDef)
        return revoluteJoint

    def __create_bodies(self):
        #Create the crawler arms
        self.bodylist.update({'arm1':self.__create_dynamic_car(290,130,0)})
        self.bodylist.update({'arm2':self.__create_dynamic_car(200,130,0)})

        #Create the crawler body
        body = self.world.CreateDynamicBody(position=(5,3.5))
        box = body.CreatePolygonFixture(box=(2.5,2.5), density=1, friction=0.8)
        self.bodylist.update({'body':body})

        #Joint connecting both arms
        ptJoint = self.bodylist['arm1'].worldCenter + self.bodylist['arm2'].worldCenter
        ptJoint = ptJoint/2

        self.jointlist.append(self.__create_joint(bodylist['arm1'],bodylist['arm2'], ptJoint))

        #Joint connceting arms and the crawler body
        ptJointB = self.bodylist['body'].worldCenter + b2Vec2(2.5,2.5) 

        self.jointlist.append(self.__create_joint(bodylist['arm2'],bodylist['body'], ptJointB))

        #Create floor
        body = self.world.CreateStaticBody(position=(0,0),shapes=polygonShape(box=(50,1)))
        self.bodylist.update({'floor':body})
    def __physicsLoop(self):
        self.world.Step(self.timeStep, self.vel_iters, self.pos_iters)

        for joint in range(len(self.jointlist)):
            actJoint = self.jointlist[joint]
            if(joint == 1):
                print(math.degrees(actJoint.angle))
                if(math.degrees(actJoint.angle) <= 30): actJoint.motorSpeed = math.radians(20.0)
                else: actJoint.motorSpeed = math.radians(0.0)
            else:
                actJoint.motorSpeed = math.radians(20.0)

    def GetJointList():
        return self.jointlist

    def GetCrawlerVelocity():
        return self.bodylist['body']

    def run(self):
        global running
        while running:
            self.ev = self.pygame.event.poll()
            keys = self.pygame.key.get_pressed()
            time.sleep(self.timeStep)
            self.__physicsLoop()
        return

bodylist={}
 
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