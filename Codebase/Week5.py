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
# The value is a list of tuples of whether a path exist and has been traveled
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
            motors.setvel(0.1, 100, 0.01)
            edge = 'l'


        elif state == 2: #Bot Centered
            motors.setvel(0.35, 0, 0.01)
            edge = 'c'


        elif state == 3: #Drifted Left
            motors.setvel(0.1, 50, 0.01)
            edge = 'l'


        elif state == 4: #Drfted far right
            motors.setvel(0.1, -100, 0.01)
            edge = 'r'


        elif state == 5: #Split in the tape
            pass


        elif state == 6: #Drifted Right
            motors.setvel(0.1, -50, 0.01)
            edge = 'r'

        #intersection found
        elif state == 7:  #Thick part of tape
            exit_condition = 1

        #print(edge)
        #print(state)

    if(exit_condition == 1):
        print("Intersection detected")
        motors.movedist(0.105)
    motors.stop()
    return(exit_condition)

def spin(motors, sensors, turn_magnitude):
    time.sleep(0.25)
    turn_magnitude = turn_magnitude % 4
    if(turn_magnitude == 3) or (turn_magnitude == -1):
        motors.angle(68, "r") #doesn't quite turn 90 degrees when asked so overcompensated
    elif(turn_magnitude == 1) or (turn_magnitude == -3):
        motors.angle(68, "l")
    elif(turn_magnitude == 2) or (turn_magnitude == -2):
        motors.angle(136, "r")
    time.sleep(0.25)
    return

#Returns array of existence of streets
#streets[0] is the street to the front of the robot
#streets[1] is the street to the left of the robot, etc. in counterclockwise order
def check(motors, sensors):
    # streets will take the form North, West, East, South
    streets = [False, False, False, False]
    # for i in range(3):
    #     state = sensors.read()
    #     if state != 0:
    #         streets[i] = True
    #     spin(motors, sensors, 1)
    #     motors.stop()
    
    # Set up check for straight, left, right, back to straight
    if Direction[-1] == "North":
        streets[4] = True
    elif Direction[-1] == "South":
        streets[1] = True
    elif Direction[-1] == "West":
        streets[3] = True
    elif Direction[-1] == "East":
        streets[2] = True

    # Check direction ahead immediately 
    state = sensors.read()
    if state != 0:
         if Direction[-1] == "North":
            streets[1] = True
        elif Direction[-1] == "South":
            streets[4] = True
        elif Direction[2] == "West":
            streets[3] = True
        elif Direction[-1] == "East":
            streets[3] = True

    
    
    spin(motors, sensors, 2)
    spin(motors, sensors, -1)
    motors.stop()
    return(streets)

# Update longitude/latitude value after a step in the given heading.
def shift(long, lat, heading):
    if heading % 4 == config.NORTH:
        return (long, lat+1)
    elif heading % 4 == config.WEST:
        return (long-1, lat)
    elif heading % 4 == config.SOUTH:
        return (long, lat-1)
    elif heading % 4 == config.EAST:
        return (long+1, lat)
    else:
        raise Exception("This can’t be")

# Find the intersection
def intersection(long, lat):
    list = [i for i in config.intersections if i.long == long and i.lat == lat]
    if len(list) == 0:
        return None
    if len(list) > 1:
        raise Exception("Multiple intersections at (%2d,%2d)" % (long, lat))
    return list[0]
    
## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    sensors = Sensor("sensors", sen_left_pin, sen_mid_pin, sen_right_pin)

    
    try:
        # # Problem 3
        # turnList = [1, 3, 3, 3, 0]
        # for turn in turnList:
        #     print("driving")
        #     if(drive(motors, sensors) == 0):
        #         print("Lost")
        #         exit
        #     print("turning")
        #     spin(motors, sensors, turn)
        # drive(motors, sensors)
        # print(check(motors, sensors))

        #Problem 5
        drive(motors, sensors)
        while True:
            # Drive forard until a corner is detected
            print("driving")
            #drive(motors,sensors)

            # Check what available paths there are
            print("Finding paths")
            paths = check(motors, sensors)
            print(paths)
            time.sleep(.5)

            # Pick the first viable path and move in that direction
            temp = 0
            for path in paths:
                if path == True:
                    print("found path")
                    print(temp)
                    if temp == 0:
                        drive(motors, sensors)
                    else:
                        spin(motors, sensors, temp)
                        drive(motors, sensors)
                    break
                else:
                    temp += 1


    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()