import threading

from numpy import average
from Motor import Motor
import time
from Sensor import Sensor
from Ultrasonic import Ultrasonic
from statistics import mean
from statistics import stdev
import random
from typing import Optional

#Define pins
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

MAX_PWM_VALUE = 254
PWM_FREQ = 1000

sen_left_pin = 14
sen_mid_pin = 15
sen_right_pin = 18

ultra_left_echo = 16
ultra_left_trig = 13
ultra_mid_echo = 20
ultra_mid_trig = 19
ultra_right_echo = 21
ultra_right_trig = 26

global stopflag


def stopcontinual():
    global stopflag 
    stopflag = True
def runcontinual():
    global stopflag
    stopflag = False
    while not stopflag:
        ULTRA_1.send_trigger()
        ULTRA_2.send_trigger()
        ULTRA_3.send_trigger()
        time.sleep(.08 + .04 * random.random())

def getUltraState(criticalDis:Optional[float] = .2):
    state = 0
    
    if ULTRA_1.get_dist() < criticalDis:
        state += 1
    if ULTRA_2.get_dist() < criticalDis:
        state += 2
    if ULTRA_3.get_dist() < criticalDis:
        state += 4

    return state

def herding():

    state = getUltraState()

    if state == 0: #no sensors detections
       motors.move(.5, .5, .02)

    elif state == 1: #left sensor trigger
        motors.move(.5, 0, .02)

    elif state == 2: #center sensor trigger
        motors.move(-.5, -.5, .02)
    
    elif state == 3: #left + center sensor trigger
        motors.move(.5, -.5, .02)

    elif state == 4: #right sensor trigger
        motors.move(0, .5, 0.02)

    elif state == 5: #right and left sensor trigger
        motors.move(-.5, -.5, .02)

    elif state == 6: #right and center sensor trigger
        motors.move(-.5, .5, .02)
  
    elif state == 7:  #all sensors triggered
        motors.move(-.5, -.5, .01)
        
def wallFollowing(wall:Optional[str]="l", d_desired:Optional[float]=0.3):
    if wall == "l":
        d = ULTRA_1.get_dist()
    else:
        d = ULTRA_3.get_dist()

    #exit if it reaches a wall in front
    if ULTRA_2.get_dist()<0.2:
        motors.stop()
        return

    #steering gain
    k = 1.5

    e = d-d_desired
    u = -k*e

    #flip correction direction if left wall is used
    if wall == "l":
        u = -u

    motors.move(max(0.5,min(0.9,0.7-u)),max(0.5,min(0.9,0.7+u)),0.02)

def advancedWallFollowing(wall:Optional[str]="l", d_desired:Optional[float]=0.3):
    if wall == "l":
        d = ULTRA_1.get_dist()
    else:
        d = ULTRA_3.get_dist()

    #exit if it reaches a wall in front
    if ULTRA_2.get_dist()<0.25:
        motors.stop()
        if wall == 'l':
            motors.angle(20,"r")
        else:
            motors.angle(20,"l")
        return

    #steering gain
    k = 1

    e = d-d_desired
    u = -k*e

    #flip correction direction if left wall is used
    if wall == "l":
        u = -u

    motors.move(max(0.5,min(0.9,0.7-u)),max(0.5,min(0.9,0.7+u)),0.02)
        

if __name__ == "__main__":
    ULTRA_1 = Ultrasonic("ULTRA_1", ultra_left_echo, ultra_left_trig)
    # Left sensor
    ULTRA_2 = Ultrasonic("ULTRA_2", ultra_mid_echo, ultra_mid_trig)
    # Middle Sensor
    ULTRA_3 = Ultrasonic("ULTRA_3", ultra_right_echo, ultra_right_trig)
    #Right Sensor

    #Initialize Motors
    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)

    #Initialize Second Thread to read sensors
    thread = threading.Thread(target=runcontinual)
    thread.start()
    
    try:

        while True:
            # ULTRA_1.send_trigger()
            # ULTRA_2.send_trigger()
            # ULTRA_3.send_trigger()
            # #wait 100 ms
            # time.sleep(0.1)

            #print("There is something " + str(ULTRA_1.get_dist()) + "m away from sensor 1")
            #print("There is something " + str(ULTRA_2.get_dist()) + "m away from sensor 2")
            #print("There is something " + str(ULTRA_3.get_dist()) + "m away from sensor 3")

            # Problem 2
            # dist = []
            # for i in range(5):
            #     ULTRA_2.send_trigger()
            #     time.sleep(.2)
            #     dist.append(ULTRA_2.get_dist())

            # avg = mean(dist)
            # dev = stdev(dist)
            # print(dist)
            # print("Mean distance " + str(avg))
            # print("Standard Deviation " + str(dev))
            # exit()

            # ## Problem 5
            # print(ULTRA_2.get_dist())
            # if ULTRA_2.get_dist() >= .2:
            #     motors.move(.5, .5, .1)
            # else:
            #     motors.stop()

            # ## Problem 6
            # herding()

            # ## Problem 7
            # wallFollowing("r",0.2)

            ## Problem 8
            advancedWallFollowing("l",0.2)


        
    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))
    
    # Exit Interupt handlers
    ULTRA_1.cbfall.cancel()
    ULTRA_2.cbfall.cancel()
    ULTRA_3.cbfall.cancel()

    ULTRA_1.cbrise.cancel()
    ULTRA_2.cbrise.cancel()
    ULTRA_3.cbrise.cancel()
    
    # Shutdown Motors
    motors.shutdown()

    # Shutdown Second Thread
    stopcontinual()
    thread.join()
        
    
