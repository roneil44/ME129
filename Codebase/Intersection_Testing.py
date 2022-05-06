## Use this file for the main codebase

# Imports

from ast import While
from sre_parse import Pattern
from turtle import right
from Motor import Motor
import time
from Sensor import Sensor
import config
from Intersection import Intersection

# Define the motor pins.
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

sen_left_pin = 14
sen_mid_pin = 15
sen_right_pin = 18

MAX_PWM_VALUE = 254
PWM_FREQ = 1000

# direction is a list that stores every direction the robot has traveled in
# the robot always assumes it travels north first and then appends the next direction
Direction = ["North"]
# Map is a dictionary where the key is the tuple of longitude and latitude
# The value is a list of available paths and a list of whether they have been explored
Map = {}


def drive(motors, sensors):
    #returns 0 at end
    #returns 1 at intersection
    #bot is centered on end criteria when block ends
    exit_condition = -1
    edge = 'c' #Set edge for sensor updates l, r or c

    while(exit_condition == -1):
        #print("here")
        state = sensors.read()

        if state == 0:
            exit_condition = 0

        elif state == 1: #Drifted far left
            motors.setvel(0.1, 50, 0.01)
            edge = 'l'


        elif state == 2: #Bot Centered
            motors.setvel(0.3, 0, 0.01)
            edge = 'c'


        elif state == 3: #Drifted Left
            motors.setvel(0.1, 25, 0.01)
            edge = 'l'


        elif state == 4: #Drfted far right
            motors.setvel(0.1, -50, 0.01)
            edge = 'r'


        elif state == 5: #Split in the tape
            pass


        elif state == 6: #Drifted Right
            motors.setvel(0.1, -25, 0.01)
            edge = 'r'

        #intersection found
        elif state == 7:  #Thick part of tape
            exit_condition = 1

        #print(edge)
        #print(state)

    motors.stop()
    time.sleep(0.5)
    if(exit_condition == 1):
        print("Intersection detected")
        motors.kick("f")
        motors.movedist(0.125,0.5)
    motors.stop()
    time.sleep(0.25)
    return(exit_condition)

def spin(motors, sensors, turn_magnitude):
    time.sleep(0.25)
    turn_magnitude = turn_magnitude % 4
    if(turn_magnitude == 3) or (turn_magnitude == -1):
        motors.angle(115, "r") #doesn't quite turn 90 degrees when asked so overcompensated
    elif(turn_magnitude == 1) or (turn_magnitude == -3):
        motors.angle(115, "l")
    elif(turn_magnitude == 2) or (turn_magnitude == -2):
        motors.angle(230, "r")
    motors.stop()
    time.sleep(0.25)

    # #update heading by converting direction to integer and using modulus
    # numeric_heading = 0
    # if Direction == "North":
    #     numeric_heading = 0
    # elif Direction == "West":
    #     numeric_heading = 1
    # elif Direction == "South":
    #     numeric_heading = 2
    # elif Direction == "East":
    #     numeric_heading = 3

    # #shift heading numerically
    # numeric_heading = ((numeric_heading+4+turn_magnitude)%4)

    # #update global direction
    # if numeric_heading == 0:
    #     Direction = "North"
    # elif numeric_heading == 1:
    #     Direction = "West"
    # elif numeric_heading == 2:
    #     Direction = "South"
    # elif numeric_heading == 3:
    #     Direction = "East"

    return

def check(motors, sensors) -> list:

    #startingDirection = Direction

    # streets will take the form North, West, South, East
    streets = [False, False, False, False]
    for i in range(3):
        motors.stop()
        time.sleep(0.25)
        state = sensors.read()
        if state != 0:
            streets[i] = True
            centerOnLine()
        motors.stop()
        time.sleep(0.25)
        spin(motors,sensors,1)

    # #perform street rotation based on starting position
    # numRotations = 0
    # if startingDirection == "North":
    #     numRotations = 0
    # elif startingDirection == "West":
    #     numRotations = 1
    # elif startingDirection == "South":
    #     numRotations = 2
    # elif startingDirection == "East":
    #     numRotations = 3

    # streets = streets[numRotations:]+streets[:numRotations]

    return(streets)

def centerOnLine():
    state = sensors.read()
    while state == 1 or state == 3 or state == 4 or state == 6:
        
        if state == 1: #Drifted far left
            motors.angle(2,'r')

        elif state == 3: #Drifted Left
            motors.angle(2,'r')

        elif state == 4: #Drfted far right
            motors.angle(2,'l')

        elif state == 6: #Drifted Right
            motors.angle(2,'l')
        
        state = sensors.read()

        if state == 2:
            motors.stop()
            time.sleep(0.25)
            state = sensors.read()

    motors.stop()
    return state


## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    sensors = Sensor("sensors", sen_left_pin, sen_mid_pin, sen_right_pin)

    
    try:

        
        #Test drive ending with check
        Direction = "North"
        turnList = [1, 3, 3, 3, 0]
        for turn in turnList:
            print("driving")
            if(drive(motors, sensors) == 0):
                print("Lost")
                exit
            print("turning")
            spin(motors, sensors, turn)
            print(Direction)
        drive(motors, sensors)
        print(check(motors, sensors))
  

    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()