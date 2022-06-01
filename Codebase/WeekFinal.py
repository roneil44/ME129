import threading

from numpy import average
from PathPlanning import nearestUnexploredDirections, pointToNearUnexplored
from Motor import Motor
import time
from Sensor import Sensor
from Ultrasonic import Ultrasonic
from statistics import mean
from statistics import stdev
import random
from typing import Optional
import pigpio

from ast import While
from curses import can_change_color
from sre_parse import Pattern
from turtle import right
import PathPlanning as path


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

# gloabl variables

# direction is a list that stores every direction the robot has traveled in
# the robot always assumes it travels north first and then appends the next direction
Direction = [0]

# coords is a global coordinate - (latitude and longitude)
coords = (0,0)

# Map is a dictionary where the key is the tuple of longitude and latitude
# The value is a list of available paths and a list of whether they have been explored
Map = {}

# state variable tracks what the bot is trying to do
# 0 - searching
# 1 - paused
# 2 - destination
# 3 - exiting
state = 0

# destination - tuple of longitude or latitude on or off the map that the bot is trying to reach
destination = (0,0)

# indicaes whether or not the current map is complete
complete = False


#Define pins
ultra_left_echo = 16
ultra_left_trig = 13
ultra_mid_echo = 20
ultra_mid_trig = 19
ultra_right_echo = 21
ultra_right_trig = 26

global driving_stopflag

def getUltraState(criticalDis:Optional[float] = .2):
    state = 0
    
    if ULTRA_1.get_dist() < criticalDis:
        state += 1
    if ULTRA_2.get_dist() < criticalDis:
        state += 2
    if ULTRA_3.get_dist() < criticalDis:
        state += 4

    return state

def drive(motors, sensors):
    #returns -1 if bot got lost
    #returns 0 at end
    #returns 1 at intersection
    #returns 2 if bot turned due to blockage

    #bot is centered on end criteria when block ends
    exit_condition = -1
    edge = 'c' #Set edge for sensor updates l, r or c

    while(exit_condition == -1):
        #print("here")
        state = sensors.read()

        if state == 0:
            find = wiggle()
            if not find:
                spiralSearch()
                return -1

        elif state == 1: #Drifted far left
            motors.setvel(0.1, 25, 0.01)
            edge = 'l'


        elif state == 2: #Bot Centered
            motors.setvel(0.2, 0, 0.01)
            edge = 'c'


        elif state == 3: #Drifted Left
            motors.setvel(0.2, 10, 0.01)
            edge = 'l'


        elif state == 4: #Drfted far right
            motors.setvel(0.2, -25, 0.01)
            edge = 'r'


        elif state == 5: #Split in the tape
            pass


        elif state == 6: #Drifted Right
            motors.setvel(0.2, -10, 0.01)
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
        motors.movedist(0.130,0.5)
    motors.stop()
    time.sleep(0.25)
    return(exit_condition)

def spiralSearch():
    Map.clear()
    print("map cleared")
    #spiral until it finds something
    left = 0.9
    rigt = 0.2
    while True:
        motors.move(left, rigt, 0.05)
        rigt += 0.001
        if rigt >= 0.9:
            rigt =0.9
        state = sensors.read()
        if state != 0:
            if state == 7:
                motors.setlinear(0.4, 'f', 0.1)
            else:
                break

    #turn to center on line
    motors.movedist(0.130,0.5)
    while True:
        motors.angle(10,"r")
        motors.stop()
        time.sleep(0.2)
        state = sensors.read()
        if state != 0:
            break
    drive(motors, sensors)
    

def wiggle():
    angle_to_turn = 15
    for i in range(4):
        motors.angle(angle_to_turn, 'r')
        motors.stop()
        time.sleep(0.25)
        if(sensors.read() != 0):
            return True
        motors.angle(angle_to_turn, 'l')
        motors.stop()
        time.sleep(0.25)
        motors.angle(angle_to_turn, 'l')
        motors.stop()
        time.sleep(0.25)
        if (sensors.read()!= 0):
            return True
        motors.angle(angle_to_turn, 'r')
        motors.stop()
        time.sleep(0.25)
        angle_to_turn += 10
    return False

def spin(motors, sensors, turn_magnitude):
    time.sleep(0.25)
    turn_magnitude = (turn_magnitude + 4) % 4
    if(turn_magnitude == 3) or (turn_magnitude == -1):
        motors.angle(100, "r") #doesn't quite turn 90 degrees when asked so overcompensated
    elif(turn_magnitude == 1) or (turn_magnitude == -3):
        motors.angle(100, "l")
    elif(turn_magnitude == 2) or (turn_magnitude == -2):
        motors.angle(100, "l")
        motors.stop()
        time.sleep(0.25)
        motors.angle(100, "l")
    motors.stop()

    # newDirection = int_to_direction((direct_to_int()+turn_magnitude+4)%4)
    # Direction.append(newDirection)

    time.sleep(0.25)
    return
    
def check(motors, sensors): 
    #Returns array of existence of streets
    #streets[0] is the street to the front of the robot
    #streets[1] is the street to the left of the robot, etc. in counterclockwise order
    # streets will take the form North, West, South, East
    streets = [False, False, False, False]
    
    # Automatically assign available path behind to true
    if Direction[-1] == 0:
        streets[2] = True
    elif Direction[-1] == 2:
        streets[0] = True
    elif Direction[-1] == 1:
        streets[3] = True
    elif Direction[-1] == 3:
        streets[1] = True

    # Check direction ahead immediately 
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == 0:
            streets[0] = True
        elif Direction[-1] == 2:
            streets[2] = True
        elif Direction[-1] == 1:
            streets[1] = True
        elif Direction[-1] == 3:
            streets[3] = True
    # Turn to the left and detect if there is a line there
    spin(motors, sensors, 1)
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == 0:
            streets[1] = True
        elif Direction[-1] == 2:
            streets[3] = True
        elif Direction[-1] == 1:
            streets[2] = True
        elif Direction[-1] == 3:
            streets[0] = True
    
    # turn 180 back to the right and update streets
    spin(motors, sensors, 1)
    centerOnLine()
    spin(motors, sensors, 1)
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == 0:
            streets[3] = True
        elif Direction[-1] == 2:
            streets[1] = True
        elif Direction[-1] == 1:
            streets[0] = True
        elif Direction[-1] == 3:
            streets[2] = True

    # Reset bot to center
    spin(motors, sensors, 1)
    state = sensors.read()
    if state!= 0:
        centerOnLine

    motors.stop()
    # motors.setlinear(0.2,"b",1.55)
    # motors.stop()
    # time.sleep(0.25)
    # drive(motors, sensors)

    return(streets)

def check_complete_map():
    #check map to see if its complete
    global complete
    if len(Map) == 0:
        complete = False

    for key in Map:
        explored = Map.get(key)
        if False in explored[1]:
            print('1')
            complete = False
            return
        else:
            print('2')
            complete = True

def centerOnLine():
    state = sensors.read()
    drive_sec = 0
    while state == 1 or state == 3 or state == 4 or state == 6:
        
        if state == 1: #Drifted far left
            motors.setspin(0.5,'r',0.01)

        elif state == 3: #Drifted Left
            motors.setspin(0.5,'r',0.01)

        elif state == 4: #Drfted far right
            motors.setspin(0.5,'l',0.01)

        elif state == 6: #Drifted Right
            motors.setspin(0.5,'l',0.01)
        
        state = sensors.read()

        if state == 2:
            #make sure its centered
            motors.setlinear(0.4, 'f', .09)
            drive_sec += .1
            state = sensors.read()
    motors.stop()
    time.sleep(0.4)
    motors.setlinear(0.4, 'b', drive_sec+0.04)
    motors.stop()
    return state

# returns whether or not the bot has completed its goals
def checkGoalComplete():

    global state
    global Map
    global destination
    global coords

    #run map check
    check_complete_map()

    #check for map completion
    if state == 0:
        if complete:
            print("Map complete")
            return True

        # # check condition for unexplored region of map blocked
        # elif nearestUnexploredDirections(Map, coords) == []:
        #     print("Map complete in current state")
        #     return True
        
        else:
            print("Still Exploring")
            return False


    elif state == 1:
        #return true as pause is complete as is
        return True

    elif state ==  2:
        #return true if arrived at destination or can't find a route
        if coords == destination:
            print("Reached Destination")
            return True

        elif complete and destination not in Map:
            print("Destination Not On Map")
            return True 

        else:
            print("Still moving towards destination")
            return False
        
    #not sure - true to enact pause
    else:
        return True

# clears all blocked element in current map definition
def resetBlockages():
    global Map
    for point in Map:
        Map[point][2] = [True, True, True, True]

# updates blockages at current position using ultrasonics and save to map 
def checkBlockages():
    critDistance = 0.3
    
    #direction of 3 ultrasonics in global orienation
    indiceMap = [(Direction[-1]+1)%4, Direction[-1], (Direction[-1]+3)%4 ]
    
    #check ultrasonics and save to list
    unBlocked = [True, True, True, True]
    if ULTRA_1.dist < critDistance:
        unBlocked[indiceMap[0]] = False
    if ULTRA_2.dist < critDistance:
        unBlocked[indiceMap[1]] = False
    if ULTRA_3.dist < critDistance:
        unBlocked[indiceMap[2]] = False

    #save list to map
    Map[coords][2] = unBlocked

def getNewDirection():

    global state
    global Map
    global coords
    global Direction

    if state == 0: #exploring
        newDirections = nearestUnexploredDirections(Map,coords)
        if newDirections == []:            
            for i in range(4):
                if Map[coords][0][i] and not Map[coords][1][i]:
                    print("returning 1")
                    return i

    elif state == 2: #moving towards target
        newDirections = pointToNearUnexplored(Map, coords,destination)

    if newDirections != []:
        print("New Directions: ")
        print(newDirections)
        return newDirections[-1]

    # if no valid new direction is loaded, bot will turn around
    print("returning 3")
    return (Direction[-1]+2)%4

def turnToDirection(newDirection):
    global Direction
    global motors
    global sensors

    print(newDirection)
    print(Direction[-1])

    turnCount = 4+newDirection-Direction[-1]
    turnCount = turnCount%4
    spin(motors, sensors, turnCount)
    Direction.append(newDirection)

def postDriveProcess(driveResults):
    global coords
    global Direction

    #shift coordinates due to successful drive
    if driveResults == 1:
        lat = coords[0]
        lon = coords[1]
        if Direction[-1] == 0:
            coords  = (lat, lon+1)   
        if Direction[-1] == 1:
            coords  = (lat-1, lon)
        if Direction[-1] == 2:
            coords  = (lat, lon-1)
        if Direction[-1] == 3:
            coords  = (lat+1, lon)

    #update blockage and flip direction
    if driveResults == 2:
        Map[coords][2][Direction[-1]] = False
        Direction.append((Direction[-1]+6)%4)

# scan new intersection and add to map
def addNewIntersection():
    availablePaths = check(motors, sensors)
    exploredPaths = [not availablePaths[0], not availablePaths[1], not availablePaths[2], not availablePaths[3]]
    unblockedPaths = [True, True, True, True]
    Map[coords] = [availablePaths,exploredPaths,unblockedPaths]

def driving_stop():
    global driving_stopflag
    driving_stopflag = True

def driving_loop():
    global driving_stopflag
    driving_stopflag = False

    while not driving_stopflag:

        print("Current Map:")
        print(Map)

        motors.stop()
        #check for goal completion conditions
        if not checkGoalComplete():
            #initialize if map is empty
            if len(Map) == 0:
                coords = (0,0)
                Direction.append(0)
                drive(motors,sensors)

            print("The map")
            print(Map)
            print("The coords")
            print(coords)
            print("Is the coords not in the map?")
            print(not coords in Map.keys())

            #scan intersection and update map
            if len(Map) == 0 or not coords in Map.keys():
                print("adding new intersection")
                addNewIntersection()
            checkBlockages()
        
            #choose new direction based on current goal and turn
            turnToDirection(getNewDirection())

            #drive and update coords/direction accordingly
            postDriveProcess(drive(motors, sensors))
            print("coords part 2")
            print(coords)
            print("Directions:")
            print(Direction)
            
            
###### User Inputs

def userinput():
    while True:
        command = input("Command ? ")
        driving_state = 0
        if (command == 'pause'):
            print ("pausing")
            driving_state = 1
        elif (command == 'explore'):
            driving_state = 0
        elif (command == 'goto'):
            target = input("target ? ")
            driving_state = 2
        elif (command == 'print'):
            print(Map)
        elif (command == 'exit'):
            print("quitting")
            driving_state = 3
        else:
            print("Unknown command '%s'" % command)
        return(driving_state)



###### Main

if __name__ == "__main__":

    io = pigpio.pi()

    ULTRA_1 = Ultrasonic("ULTRA_1", io, ultra_left_echo, ultra_left_trig)
    # Left sensor
    ULTRA_2 = Ultrasonic("ULTRA_2", io, ultra_mid_echo, ultra_mid_trig)
    # Middle Sensor
    ULTRA_3 = Ultrasonic("ULTRA_3", io, ultra_right_echo, ultra_right_trig)
    #Right Sensor

    #Initialize Motors
    motors = Motor("motors", io, MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)

    #Initialize Infared
    sensors = Sensor("sensors", io, sen_left_pin, sen_mid_pin, sen_right_pin)

    #Initialize Second Thread to read sensors
    ULTRA_1.start()
    ULTRA_2.start()
    ULTRA_3.start()

    driving_thread = threading.Thread(target=driving_loop)
    driving_thread.start()

    try:
        state = userinput()
        if state == 3:
            exit()
        
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
    ULTRA_1.stopcontinual()
    ULTRA_2.stopcontinual()
    ULTRA_3.stopcontinual()