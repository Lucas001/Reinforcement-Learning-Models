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

        self.screenX = 800
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
        self.reward = -0.08

        self.rl_body_linVelocity = 0.0;
        self.rl_generation = 0
        self.body_last_pos = b2Vec2(-1,-1)
        #Creation of matrix with 10 possible angles
        w, h = 10, 10 
        self.matrix_states = [[0 for x in range(w)] for y in range(h)] 
        #Creation of matrix with the actions
        self.matrix_policy = [["." for x in range(w)] for y in range(h)]
        #Creation of matrix with the visit count, to compute the gain of the exploite
        self.matrix_visits = [[1 for x in range(w)] for y in range(h)]

        #Gain constant, since the max reward is 3.5 (max dislocation)
        self.gain = 0.02
        self.alpha = 1

    def calculateNextAction(self, crawlerPos, joint_angles):
        action = []

        if(self.rl_generation == 0):
            self.body_last_pos = crawlerPos.x
        else:
            self.rl_body_linVelocity = (crawlerPos.x - self.body_last_pos)
            self.body_last_pos = crawlerPos.x


        i,j = int(joint_angles[0]/6.0 -1),int(joint_angles[1]/6.0 -1)
        if(i > len(self.matrix_states)-1): i = len(self.matrix_states)-1
        if(j > len(self.matrix_states)-1): j = len(self.matrix_states)-1
        if(i < 0): i = 0
        if(j < 0): j = 0

        print("angles: %d, %d" %(i,j))


        #self.adjustStateValues()
        self.matrix_visits[i][j] += 1

        print("State-Values:")
        for k in range(0,10):
            print("")
            for w in range(0,10):
                output = 1000*self.matrix_states[k][w]
                #output = self.matrix_visits[k][w]
                print("%.2f\t" % output, end = "")

        print ("\n\n")

        print("Policy:")
        for k in range(0,10):
            print("")
            for w in range(0,10):
                output = self.matrix_policy[k][w]
                #output = self.matrix_visits[k][w]
                print("%s\t" % output, end = "")

        print ("\n\n")
        #print([[ print("%.2f\t" % self.matrix_states[k][w]) for k in range(0,9)] for w in range(0,9)])
        #print(self.matrix_states)
        action = self.calculateStateValue(i,j)

        self.rl_generation += 1

        self.alpha += 1
        return action

    def adjustStateValue(self, i, j):
        return (self.matrix_states[i][j] + self.gain/self.matrix_visits[i][j])
    
    def calculateStateValue(self, i , j):
#Actions:
#01 - Arm 2 activated +
#02 - Arm 2 activated -
#10 - Arm 1 activated +
#11 - Both arms activated +
#12 - Arm 1 + | Arm 2 -
#20 - Arm 1 -
#21 - Arm 1 - | Arm 2 +
#22 - Both arms activated -
        max_ind = len(self.matrix_states) - 1
        possible_state_values = []
        possible_actions = []

        for action in range(0,8):
            fut_state = []
            if(action == 0):
                fut_state.extend([i,j + 1])
                possible_actions.append("01")
            if(action == 1):
                fut_state.extend([i,j - 1])
                possible_actions.append("02")
            if(action == 2):
                fut_state.extend([i + 1,j])
                possible_actions.append("10")
            if(action == 3):
                fut_state.extend([i + 1,j + 1])
                possible_actions.append("11")
            if(action == 4):
                fut_state.extend([i + 1,j - 1])
                possible_actions.append("12")
            if(action == 5):
                fut_state.extend([i - 1,j])
                possible_actions.append("20")
            if(action == 6):
                fut_state.extend([i - 1,j + 1])
                possible_actions.append("21")
            if(action == 7):
                fut_state.extend([i - 1,j - 1])
                possible_actions.append("22")

            if(fut_state[0] < 0 or fut_state[1] < 0 or fut_state[0] > max_ind or fut_state[1] > max_ind): 
                possible_state_values.append(-100000)
            else:
                act_state = []
                act_state.append(i)
                act_state.append(j)
                possible_state_values.append(self.calculateLocalQStates(fut_state, act_state))

        print(possible_actions)
        max_value = -99999
        max_action = ""
        for action in range(0,8):
            if(possible_state_values[action] > max_value):
                max_value = possible_state_values[action]
                max_action = possible_actions[action]

        self.matrix_states[i][j] = max_value
        self.matrix_policy[i][j] = max_action

        return max_action

    def calculateLocalQStates(self, fut_state, act_state):
        return (1 - 1/self.matrix_visits[act_state[0]][act_state[1]])*self.matrix_states[act_state[0]][act_state[1]] + 1/self.matrix_visits[act_state[0]][act_state[1]]*(self.reward + self.rl_body_linVelocity + self.discount*self.adjustStateValue(fut_state[0],fut_state[1]))

    def GetGeneration(self):
        return self.rl_generation

class Physics(Thread):
    def __init__(self, outPygame, outEv, outBodyList):
        Thread.__init__(self)
        self.pygame_box2d_ratio=20.0
        self.world = b2World(gravity=(0,-10), doSleep=True)
        self.timeStep = 1.0 / 300
        self.vel_iters = 3
        self.pos_iters = 1
        self.car_x_size = 3.0
        self.car_y_size = 0.5
        self.bodylist = outBodyList
        self.jointlist = []
        self.ev = outEv
        self.pygame = outPygame
        self.rl_algorithm = ReinforcementLearning()

        self.reaching_angle = [False for i in range(0,2)]
        self.reached_angle = [False for i in range(0,2)]
        self.angle_to_reach = [0 for i in range(0,2)]
        self.calc_actions = []

        self.__create_bodies()

    def __create_dynamic_car(self,xpos,ypos):
        body= self.world.CreateDynamicBody(position=(xpos/self.pygame_box2d_ratio,ypos/self.pygame_box2d_ratio))
        box=body.CreatePolygonFixture(box=(self.car_x_size/2.0,self.car_y_size/2.0), density=0.005, friction=100000)
        body.linearVelocity=(0,0)
        body.angularDamping=0.0
        return body

    def __create_joint(self, body1, body2, ptJoint, conCollision):
        jointDef = b2RevoluteJointDef()
        jointDef.Initialize(body1, body2, ptJoint)
        jointDef.collideConnected = conCollision
        jointDef.lowerAngle = 00
        jointDef.upperAngle = math.radians(60)
        jointDef.enableLimit = True
        jointDef.maxMotorTorque = 50000
        #jointDef.motorToque = 50000
        jointDef.motorSpeed = 0
        jointDef.enableMotor = True

        revoluteJoint = self.world.CreateJoint(jointDef)
        return revoluteJoint

    def __create_bodies(self):
        #Create the crawler arms
        self.bodylist.update({"arm1":self.__create_dynamic_car(270,130)})
        self.bodylist.update({'arm2':self.__create_dynamic_car(190,130)})
        
        

        #Create the crawler body
        body = self.world.CreateDynamicBody(position=(5,3.5))
        box = body.CreatePolygonFixture(box=(2.5,2.5), density=0.07, friction=1.5)
        self.bodylist.update({'body':body})

        #Joint connceting arms and the crawler body
        ptJointB = self.bodylist['body'].worldCenter + b2Vec2(2.5,2.5) 

        self.jointlist.append(self.__create_joint(bodylist['arm2'],bodylist['body'], ptJointB,True))

        #Joint connecting both arms
        ptJoint = self.bodylist['arm1'].worldCenter + self.bodylist['arm2'].worldCenter
        ptJoint = ptJoint/2

        self.jointlist.append(self.__create_joint(bodylist['arm1'],bodylist['arm2'], ptJoint,False))

        #Create floor
        body = self.world.CreateStaticBody(position=(0,0),shapes=polygonShape(box=(1000,1)))
        self.bodylist.update({'floor':body})

    def __physicsLoop(self):
        joint_angles = [math.degrees(self.jointlist[i].angle) for i in range(len(self.jointlist))]
        crawler_pos = self.bodylist['body'].worldCenter
        if(self.reaching_angle[0] is not True and self.reaching_angle[1] is not True):
            self.actions = self.rl_algorithm.calculateNextAction(crawler_pos,joint_angles)
            print(self.rl_algorithm.GetGeneration())

        for joint in range(len(self.jointlist)):
            #print(joint)
            actJoint = self.jointlist[joint]
            if(self.actions[joint] == "1"):
                if(self.reaching_angle[joint] is not True): 
                    self.angle_to_reach[joint] = math.degrees(self.jointlist[joint].angle) + 6
                    actJoint.lowerAngle = self.jointlist[joint].angle - math.radians(2)
                    actJoint.upperAngle = math.radians(self.angle_to_reach[joint]+2)
                    if(self.angle_to_reach[joint] > 60.0): self.angle_to_reach[joint] = 60.0
                    self.reaching_angle[joint] = True
                
                if(math.degrees(actJoint.angle) <= self.angle_to_reach[joint]): actJoint.motorSpeed = math.radians(20.0)
                else:
                    self.reaching_angle[joint] = False 
                    actJoint.motorSpeed = math.radians(0.0)

            if(self.actions[joint] == "2"):
                if(self.reaching_angle[joint] is not True): 
                    self.angle_to_reach[joint] = math.degrees(self.jointlist[joint].angle) - 6
                    actJoint.upperAngle = self.jointlist[joint].angle + math.radians(2)
                    actJoint.lowerAngle = math.radians(self.angle_to_reach[joint]-2)
                    if(self.angle_to_reach[joint] < 0.0): self.angle_to_reach[joint] = 0.0
                    self.reaching_angle[joint] = True

                if(math.degrees(actJoint.angle) >= self.angle_to_reach[joint]): actJoint.motorSpeed = math.radians(-20.0)
                else:
                    self.reaching_angle[joint] = False 
                    actJoint.motorSpeed = math.radians(0.0)

        self.world.Step(self.timeStep, self.vel_iters, self.pos_iters)

    def run(self):
        global running
        while running:
            self.ev = self.pygame.event.poll()
            keys = self.pygame.key.get_pressed()
            time.sleep(1/10*self.timeStep)
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
