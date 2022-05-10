## Use this file for the main codebase

# Imports

from ast import While
from pickle import FALSE, TRUE
from turtle import right
import time
import config
import random


# Map is a dictionary where the key is the tuple of longitude and latitude
# The value is a list of available paths and a list of whether they have been explored



def get_map(coords):
    # This function checks to see if the bot has been to this location
    # if it hasn't been it calls check and adds the current intersection to the map
    # Also generates a list of whether each path has been traveled in the order
    # North, West, South, East

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
        print("Here")
        Map[coords] = [available_paths, explored_paths]
        return Map[coords]
    
def shift(coords, Direction):
    # Update longitude/latitude value after a step in the given heading.
    if Direction == 0:
        (long, lat) = coords
        lat += 1
        coords = (long, lat)
        return (coords)
    elif Direction == 1:
        (long, lat) = coords
        long -= 1
        coords = (long, lat)
        return (coords)
    elif Direction == 2:
        (long, lat) = coords
        lat -= 1
        coords = (long, lat)
        return (coords)
    elif Direction == 3:
        (long, lat) = coords
        long += 1
        coords = (long, lat)
        return (coords)
    else:
        raise Exception("Error in shift")


## Main Body
if __name__ == '__main__':

    Map = {\
        (0, 0):[[True, False, False, True], [True, False, False, True]], \
        (1, 0):[[True, True, False, True], [True, True, False, True]], \
        (2, 0):[[True, True, False, False], [True, True, False, False]], \
        (0, 1):[[True, False, True, False], [True, False, True, False]], \
        (1, 1):[[False, False, True, True], [False, False, True, True]], \
        (2, 1):[[True, True, True, False], [True, True, True, False]], \
        (0, 2):[[False, False, True, True], [False, False, True, True]], \
        (1, 2):[[True, True, False, True], [True, True, False, True]], \
        (2, 2):[[True, True, True, False], [True, True, True, False]], \
        (0, 3):[[True, False, False, True], [True, False, False, True]], \
        (1, 3):[[True, True, True, True], [True, True, True, True]], \
        (2, 3):[[False, True, True, False], [False, True, True, False]], \
        (0, 4):[[False, False, True, True], [False, False, True, True]], \
        (1, 4):[[False, True, True, False], [False, True, True, False]]}

    StartingPosition = (0,0)
    Destination = (0,4)

    #create directions map with starting positon and empty directions hisotry
    Directions = {StartingPosition: []}
    
    searching = TRUE
    coordsTraveled = [StartingPosition]

    while searching == TRUE:
        
        # iterate through all current paths where keys
        # are coordinates where the path ends and value is path
        newDirections = {}

        for currentCoords in Directions.keys():

            connections = Map.get(currentCoords)[0]
            explored    = Map.get(currentCoords)[1]
            
            for i in range(4):
                if connections[i] and explored[i]:
                    newCoordinate = shift(currentCoords,i)
                    if newCoordinate in coordsTraveled:
                        pass
                    else:
                        newDirections[newCoordinate] = Directions[currentCoords]+[i]
                        coordsTraveled.append(newCoordinate)

        #replace directions dictionary with updated directions one step further        
        Directions = newDirections

        print(Directions)
        time.sleep(3)

        if Destination in Directions.keys():
            searching = FALSE
            print("Route Found")
    
    print(Directions.get(Destination))