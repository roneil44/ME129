import threading

from numpy import average
from Week6 import drive_route
from PathPlanning import pointToPointDirections, targetedExploringDirections, efficientExploringDirections, getDeadEndList
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
import ast


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
    turned_around = False #tracks if we ran into an obstacle or not

    while(exit_condition == -1):
        ultra_state = getUltraState(0.1)
        #print("here")
        state = sensors.read()

        if state == 0:

            if ULTRA_1.dist<0.3 and ULTRA_3.dist<0.3:
                #steering gain
                k = 1.5
                
                #error
                e = ULTRA_3.dist-ULTRA_1.dist
                u = -k*e
                
                motors.move(max(0.5,min(0.9,0.7-u)),max(0.5,min(0.9,0.7+u)),0.02)
    
            else:

                find = wiggle()
                if not find:
                    spiralSearch()
                    return -1

        elif state == 1: #Drifted far left
            motors.setvel(0.1, 25, 0.01)
            edge = 'l'


        elif state == 2: #Bot Centered
            if ultra_state == 2 or ultra_state == 3 or ultra_state == 7:
                #all cases where middle sensor sees something in front
                print("obstacle found")
                motors.stop()
                motors.angle(200) #spin 180 
                turned_around = True
            else:
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
            #if ULTRA_1.dist<0.3 and ULTRA_3.dist<0.3:
                #only go forward?
                #exit_condition = 3
                #pass
            #else:
            if turned_around:
                exit_condition = 2
            else:
                exit_condition = 1

        #print(edge)
        #print(state)

    motors.stop()
    time.sleep(0.5)
    if(exit_condition == 1 or exit_condition == 2):
        print("Intersection detected")
        motors.movedist(0.130,0.5)
    motors.stop()
    time.sleep(0.25)
    print(exit_condition)
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
        motors.angle(angle_to_turn+5, 'r')
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
        if (sensors.read() != 0):
            return True
        motors.angle(angle_to_turn + 5, 'r')
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
            complete = False
            return
        else:
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
            return False

        # # check condition for unexplored region of map blocked
        # elif nearestUnexploredDirections(Map, coords) == []:
        #     print("Map complete in current state")
        #     return True
        
        else:
            print("Still Exploring")
            return False


    elif state == 1:
        #return true as pause is complete as is
        time.sleep(2)
        state = 0
        return False

    elif state ==  2:
        #return true if arrived at destination or can't find a route
        if coords == destination:
            print("Reached Destination")
            return True

        elif complete and destination not in Map:
            print("Destination Not On Map going to closest")
            return True 

        else:
            print("Moving towards destination")
            #drive_route(Map, Direction[-1], coords, destination)
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
    #motors.movedist(-0.130,0.5)
    unBlocked = Map[coords][2]
    if ULTRA_1.dist < critDistance:
        unBlocked[indiceMap[0]] = False
    if ULTRA_2.dist < critDistance:
        unBlocked[indiceMap[1]] = False
    if ULTRA_3.dist < critDistance:
        unBlocked[indiceMap[2]] = False

    #save list to map
    Map[coords][2] = unBlocked
    # motors.movedist(0.130,0.5)
    motors.stop()

def getNewDirection():

    global state
    global Map
    global coords
    global Direction

    if state == 0: #exploring
        newDirections = efficientExploringDirections(Map,coords)
        if len(newDirections) == 0:
            resetBlockages()
            newDirections = efficientExploringDirections(Map,coords)

    elif state == 2: #moving towards target
        newDirections = targetedExploringDirections(Map,coords, destination)
        if len(newDirections) == 0:
            resetBlockages()
            newDirections = targetedExploringDirections(Map,coords, destination)

    if newDirections != []:
        print("New Directions: "+str(newDirections))
        return newDirections[0]

    # if no valid new direction is loaded, bot will turn around
    return (Direction[-1]+2)%4

def turnToDirection(newDirection):
    global Direction
    global motors
    global sensors


    turnCount = 4+newDirection-Direction[-1]
    turnCount = turnCount%4
    spin(motors, sensors, turnCount)
    Direction.append(newDirection)

def postDriveProcess(driveResults):
    global coords
    global Direction
    global Map

    #shift coordinates due to successful drive
    if driveResults == 1:

        lat = coords[0]
        lon = coords[1]
        if Direction[-1] == 0:
            coords  = (lat, lon+1)   
        elif Direction[-1] == 1:
            coords  = (lat-1, lon)
        elif Direction[-1] == 2:
            coords  = (lat, lon-1)
        elif Direction[-1] == 3:
            coords  = (lat+1, lon)
        else:
            print("DIRECTIONS CALL ERROR")

    elif driveResults == 2:
        Map[coords][2][Direction[-1]] = False
        Direction.append((Direction[-1]+6)%4)
        Map[coords][1][(2+Direction[-1])%4] = True

# scan new intersection and add to map
def addNewIntersection():
    availablePaths = check(motors, sensors)
    exploredPaths = [not availablePaths[0], not availablePaths[1], not availablePaths[2], not availablePaths[3]]
    unblockedPaths = [True, True, True, True]
    Map[coords] = [availablePaths,exploredPaths,unblockedPaths]

def updateTraveledPaths():
    global coords
    global Map
    global Direction

    lat = coords[0]
    lon = coords[1]

    if Direction[-1] == 0:
        previousCoords  = (lat, lon-1)   
    elif Direction[-1] == 1:
        previousCoords  = (lat+1, lon)
    elif Direction[-1] == 2:
        previousCoords  = (lat, lon+1)
    elif Direction[-1] == 3:
        previousCoords  = (lat-1, lon)

    if previousCoords in Map and coords in Map:
        Map[previousCoords][1][Direction[-1]] = True
        Map[coords][1][(2+Direction[-1])%4] = True

def driving_stop():
    global driving_stopflag
    driving_stopflag = True

def driving_loop():
    global driving_stopflag
    global coords
    driving_stopflag = False

    while not driving_stopflag:
        motors.stop()
        #check for goal completion conditions
        if not checkGoalComplete():
            #initialize if map is empty
            if len(Map) == 0:
                coords = (0,0)
                Direction.append(0)
                drive(motors,sensors)

            #scan intersection and update map
            if len(Map) == 0 or not coords in Map.keys():
                addNewIntersection()
            checkBlockages()
            updateTraveledPaths()
        
            #choose new direction based on current goal and turn
            turnToDirection(getNewDirection())

            #drive and update coords/direction accordingly
            postDriveProcess(drive(motors, sensors))
            

###### User Inputs

def userinput():
    global state
    global Map
    global Direction
    global destination

    while True:
        
        command = input("Command ? ")
        state = 0
        if (command == 'pause'):
            print ("pausing")
            state = 1
        elif (command == 'explore'):
            state = 0
        elif (command == 'goto'):
            target = input("target ? ")
            temp = target.split()
            long = temp[0]
            lat = temp[1]
            state = 2
            destination = (long,lat)
        elif (command == 'print'):
            print(Map)
        elif (command == 'exit'):
            print("quitting")
            state = 3
            break
        elif (command == 'save'):
            with open("Map.txt","w") as f:
                for key, value in Map.items():
                    f.write('%s:%s\n' % (key, value))
            print("saved map")
        elif (command == 'load'):
            with open("Map2.txt") as f:
                data = f.read()
                Map = ast.literal_eval(data)
                print(Map)
        elif (command == 'home'):
            Map.clear()
            Direction = [0]
            print("cleared map")
            state = 4
        else:
            print("Unknown command '%s'" % command)



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

    #stop the driving thread
    driving_stop()

    # Exit Interupt handlers
    ULTRA_1.cbfall.cancel()
    ULTRA_2.cbfall.cancel()
    ULTRA_3.cbfall.cancel()

    ULTRA_1.cbrise.cancel()
    ULTRA_2.cbrise.cancel()
    ULTRA_3.cbrise.cancel()

    #Write Map
    with open("Map.txt","w") as f:
        for key, value in Map.items():
            f.write('%s:%s\n' % (key, value))


    # Shutdown Motors
    motors.shutdown()

    # Shutdown Second Thread
    ULTRA_1.stopcontinual()
    ULTRA_2.stopcontinual()
    ULTRA_3.stopcontinual()

    