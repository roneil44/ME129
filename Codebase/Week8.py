import threading

from numpy import average
from PathPlanning import nearestUnexploredDirections
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

# direction is a list that stores every direction the robot has traveled in
# the robot always assumes it travels north first and then appends the next direction
Direction = ["North"]
# Map is a dictionary where the key is the tuple of longitude and latitude
# The value is a list of available paths and a list of whether they have been explored
Map = {}

complete = False
Dead_End_List = []

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
        

###### Line Following Drive and Mapping Functions

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
            find = wiggle()
            if not find:
                #clear map
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

def updateDeadEndList():
    global Dead_End_List
    
    Dead_End_List = []

    for point in Map:
        streets = Map.get(point)[0]
        sum = 0
        for i in range(4):
            if streets[i]:
                sum+= 1
        if(sum == 4):
            Dead_End_List.append(point)
    
def check(motors, sensors): 
    #Returns array of existence of streets
    #streets[0] is the street to the front of the robot
    #streets[1] is the street to the left of the robot, etc. in counterclockwise order
    # streets will take the form North, West, South, East
    streets = [False, False, False, False]
    # for i in range(3):
    #     state = sensors.read()
    #     if state != 0:
    #         streets[i] = True
    #     spin(motors, sensors, 1)
    #     motors.stop()
    
    # Automatically assign available path behind to true
    if Direction[-1] == "North":
        streets[2] = True
    elif Direction[-1] == "South":
        streets[0] = True
    elif Direction[-1] == "West":
        streets[3] = True
    elif Direction[-1] == "East":
        streets[1] = True

    # Check direction ahead immediately 
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == "North":
            streets[0] = True
        elif Direction[-1] == "South":
            streets[2] = True
        elif Direction[-1] == "West":
            streets[1] = True
        elif Direction[-1] == "East":
            streets[3] = True
    # Turn to the left and detect if there is a line there
    spin(motors, sensors, 1)
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == "North":
            streets[1] = True
        elif Direction[-1] == "South":
            streets[3] = True
        elif Direction[-1] == "West":
            streets[2] = True
        elif Direction[-1] == "East":
            streets[0] = True
    
    # turn 180 back to the right and update streets
    spin(motors, sensors, 1)
    centerOnLine()
    spin(motors, sensors, 1)
    state = sensors.read()
    if state != 0:
        centerOnLine()
        if Direction[-1] == "North":
            streets[3] = True
        elif Direction[-1] == "South":
            streets[1] = True
        elif Direction[-1] == "West":
            streets[0] = True
        elif Direction[-1] == "East":
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

def choose_unexplored_direction(coords):
    #get potential paths
    temp = []
    temp = get_map(coords)
    available_paths = temp[0]
    explored_paths = temp[1]


    # treat unavailable paths as explored
    for a in range(4):
        if available_paths[a] == False:
            explored_paths[a] = True
    
    
    # create a list that stores which paths are unexplored
    unexplored = []
    available = []
    both = []
    
    for i in range(4):
        if explored_paths[i] == False:
            unexplored.append(i)
    
    for k in range(4):
        if available_paths[k] == True:
            available.append(k)
      
    
    for j in range(4):
        if explored_paths[j] == False and available_paths[j] == True:
            both.append(j)
    
    if len(unexplored) == 0:
        closestNodeRoute = path.nearestUnexploredDirections(Map, coords)
        if len(closestNodeRoute) == 0:
            next_dir = random.choice(available)
        else:
            next_dir = closestNodeRoute[0]
    else:# If there are unexplored paths choose the first one
        next_dir = both[0]
    # Convert current direction to integer
    current = direct_to_int()

    # Find difference between current direction and desired direction
    change = next_dir - current
    spin(motors, sensors, change)

    #Direction update moved to SPIN function
    
    # Append next direction to directions list
    update = int_to_direction(next_dir)
    Direction.append(update)

    check_complete_map()

    #Set current path to explored
    explored_paths[next_dir] = True
    Map[coords] = [available_paths, explored_paths]

def check_complete_map():
    #check map to see if its complete
    global complete
    for key in Map:
        explored = Map.get(key)
        print(Map)
        if False in explored[1]:
            print('1')
            complete = False
            return
        else:
            print('2')
            complete = True
            
def direct_to_int():
    if Direction[-1] == "North":
        return 0
    elif Direction[-1] == "West":
        return 1
    elif Direction[-1] == "South":
        return 2
    elif Direction[-1] == "East":
        return 3
    else:
        raise Exception("Invaalid previous direction")

def int_to_direction(dir: int):
    if dir == 0:
        return "North"
    elif dir == 1:
        return "West"
    elif dir == 2:
        return "South"
    elif dir == 3:
        return "East"
    else:
        raise Exception("Invalid new direction")

def get_map(coords):
    # This function checks to see if the bot has been to this location
    # if it hasn't been it calls check and adds the current intersection to the map
    # Also generates a list of whether each path has been traveled in the order
    # North, West, South, East
    
    if coords in Map:
        print("known intersection")
        temp = Map[coords]
        explored_paths = temp[1]
        if Direction[-1] == "North":
            explored_paths[2] = True
        elif Direction[-1] == "South":
            explored_paths[0] = True
        elif Direction[-1] == "West":
            explored_paths[3] = True
        elif Direction[-1] == "East":
            explored_paths[1] = True
        return Map[coords]
        
    else:
        explored_paths = [False, False, False, False]
        # Add path traveled to get to the instersection as true
        if Direction[-1] == "North":
            explored_paths[2] = True
        elif Direction[-1] == "South":
            explored_paths[0] = True
        elif Direction[-1] == "West":
            explored_paths[3] = True
        elif Direction[-1] == "East":
            explored_paths[1] = True
        print("unknown intersection")
        available_paths = check(motors, sensors)
        Map[coords] = [available_paths, explored_paths]
        return Map[coords]
      
def shift(coords):
    # Update longitude/latitude value after a step in the given heading.
    if Direction[-1] == "North":
        (long, lat) = coords
        lat += 1
        coords = (long, lat)
        return (coords)
    elif Direction[-1] == "West":
        (long, lat) = coords
        long -= 1
        coords = (long, lat)
        return (coords)
    elif Direction[-1] == "South":
        (long, lat) = coords
        lat -= 1
        coords = (long, lat)
        return (coords)
    elif Direction[-1] == "East":
        (long, lat) = coords
        long += 1
        coords = (long, lat)
        return (coords)
    else:
        raise Exception("This cant be")

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

def drive_route(map, curr_heading, start_point, end_point):
    headings = path.pointToPointDirections(map, start_point, end_point)
    print(headings)
    print(curr_heading)
    for next_dir in headings:
        
        # Find difference between current direction and desired direction, then turn in that direction
        change = next_dir - curr_heading
        print(change)
        spin(motors, sensors, change)
        
        # Drive until intersection
        drive(motors, sensors)
        # Now "next direction" is current direction
        curr_heading = next_dir
    
    Direction.append(int_to_direction(curr_heading))

def followroute(headings):
    curr_heading = Direction[-1]

    for next_dir in headings:
        
        # Find difference between current direction and desired direction, then turn in that direction
        change = next_dir - curr_heading
        print(change)
        spin(motors, sensors, change)
        
        # Drive until intersection
        drive(motors, sensors)
        # Now "next direction" is current direction
        curr_heading = next_dir
    
    Direction.append(int_to_direction(curr_heading))


def driving_stop():
    global driving_stopflag
    driving_stopflag = True
def driving_loop():
    global driving_stopflag
    driving_stopflag = False

    while not driving_stopflag:
        drive(motors, sensors)
        coords = (0, 0)
        unexplored = True
        if nearestUnexploredDirections(Map, coords) == []:
            choose_unexplored_direction(coords)
            coords = shift(coords)
        else:
            nearestUnexploredDirections(Map, coords)
            
        
            
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
        
    
