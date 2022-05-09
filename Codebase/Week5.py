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
            raise Exception("LOST")

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
        motors.movedist(0.108,0.5)
    motors.stop()
    time.sleep(0.25)
    return(exit_condition)

def spin(motors, sensors, turn_magnitude):
    time.sleep(0.25)
    turn_magnitude = turn_magnitude % 4
    if(turn_magnitude == 3) or (turn_magnitude == -1):
        motors.angle(90, "r") #doesn't quite turn 90 degrees when asked so overcompensated
    elif(turn_magnitude == 1) or (turn_magnitude == -3):
        motors.angle(90, "l")
    elif(turn_magnitude == 2) or (turn_magnitude == -2):
        motors.angle(180, "r")
    motors.stop()
    time.sleep(0.25)
    return

#Returns array of existence of streets
#streets[0] is the street to the front of the robot
#streets[1] is the street to the left of the robot, etc. in counterclockwise order
def check(motors, sensors): 
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
    print("here")
    available_paths = temp[0]
    explored_paths = temp[1]

    print(available_paths)
    print(explored_paths)

    # treat unavailable paths as explored
    for a in range(4):
        if available_paths[a] == False:
            explored_paths[a] = True
    
    print(explored_paths)
    
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
    

    # If all avaialble paths have been explored move in the first available direction
    # currently prioritizes North -> West -> South -> East
    print(unexplored)
    print(available)
    print(both)

    if len(unexplored) == 0:
        next_dir = available[0]
    else:# If there are unexplored paths choose the first one
        next_dir = both[0]
    # Convert current direction to integer
    current = direct_to_int()

    # Find difference between current direction and desired direction
    change = next_dir - current
    print(next_dir)
    spin(motors, sensors, change)

    # Append next direction to directions list
    update = int_to_direction(next_dir)
    print(update)
    print("should drive forward now")
    Direction.append(update)

    #Set current path to explored
    explored_paths[next_dir] = True
    Map[coords] = [available_paths, explored_paths]
    


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

    print(coords)
    print(Map)
    
    
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
        print("unknown intersection")
        available_paths = check(motors, sensors)
        print("Here")
        Map[coords] = [available_paths, explored_paths]
        return Map[coords]

        

# Update longitude/latitude value after a step in the given heading.
def shift(coords):
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

# Find the intersection
def intersection(long, lat):
    list = [i for i in config.intersections if i.long == long and i.lat == lat]
    if len(list) == 0:
        return None
    if len(list) > 1:
        raise Exception("Multiple intersections at (%2d,%2d)" % (long, lat))
    return list[0]
    
def centerOnLine():
    state = sensors.read()
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

        
        # if drive(motors, sensors) == 1:
        #     print(check(motors, sensors))

        # drive(motors, sensors)
        # spin(motors, sensors, 1)
        # spin(motors, sensors, 3)


        #Problem 5
        drive(motors, sensors)
        coords = (0, 0)
        while True:
            # Drive forard until a corner is detected
            print("driving from")
            print(coords)
            print(Direction)
            print("\n")
            # Check what available paths there are
            print("Finding paths")
            choose_unexplored_direction(coords)
            drive(motors,sensors)
            print(Direction)
            coords = shift(coords)
            


        # spin(motors, sensors, 3)
        # spin(motors, sensors, 1)

        # Problem 3
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


        # #Problem 5
        # drive(motors, sensors)
        # while True:
        #     # Drive forard until a corner is detected
        #     print("driving")
        #     #drive(motors,sensors)

        #     # Check what available paths there are
        #     print("Finding paths")
        #     paths = check(motors, sensors)
        #     print(paths)
        #     time.sleep(.5)

        #     # Pick the first viable path and move in that direction
        #     temp = 0
        #     for path in paths:
        #         if path == True:
        #             print("found path")
        #             print(temp)
        #             if temp == 0:
        #                 drive(motors, sensors)
        #             else:
        #                 spin(motors, sensors, temp)
        #                 drive(motors, sensors)
        #             break
        #         else:
        #             temp += 1
  

    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()