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


def pointToPointDirections(Map, StartingPosition, Destination):
    # Directions dictionary holds all possible routes to the destination
    # Key is where each path currently ends and key value is the list of turns to get there
    
    # Directions is initialized with starting position and an empty list of turns to get there
    Directions = {StartingPosition: []}
    
    # variable to indicate route search is still in progress
    searching = TRUE

    # keeps list of coordinates that pathes have already crosses so pathes won't
    # backtrack or follow other redundant pathes
    coordsMapped = [StartingPosition]

    #main loop that propogates the dictionary
    while searching == TRUE:
        
        # iterate through all current paths extending them to new valid coordinates
        # saves to new dictionary of directions
        newDirections = {}

        # loop starts with every known path
        for currentCoords in Directions.keys():
            
            # loads map data at this point
            connections = Map.get(currentCoords)[0]
            explored    = Map.get(currentCoords)[1]
            
            # for loop will try and create a new path by extending in available directions
            # which are existant, already explored, and the where the new coordinate is on the map
            # but not added to the coordsMapped list (list of coordinates already on existing pathes)
            for i in range(4):
                if connections[i] and explored[i]:
                    newCoordinate = shift(currentCoords,i)
                    if newCoordinate in coordsMapped:
                        pass
                    elif newCoordinate in Map:
                        newDirections[newCoordinate] = Directions[currentCoords]+[i]
                        coordsMapped.append(newCoordinate)

        # replace directions dictionary with updated directions one step further        
        Directions = newDirections

        # checks for all routes being terminated before reaching desintation
        if len(Directions) == 0:
            searching = FALSE
            print("No Route Found")

        # checks for any routes that found the destinations
        if Destination in Directions.keys():
            searching = FALSE
            print("Route Found")
    
    #prints output path if available
    if len(Directions) == 0:
        pass
        return([])
    else:
        print(Directions.get(Destination))
        return(Directions.get(Destination))
    
def nearestUnexploredDirections(Map, StartingPosition):
    # Directions dictionary holds all possible routes to the destination
    # Key is where each path currently ends and key value is the list of turns to get there
    
    # Directions is initialized with starting position and an empty list of turns to get there
    Directions = {StartingPosition: []}
    
    # variable to indicate route search is still in progress
    searching = TRUE

    # keeps list of coordinates that pathes have already crosses so pathes won't
    # backtrack or follow other redundant pathes
    coordsMapped = [StartingPosition]

    #main loop that propogates the dictionary
    while searching == TRUE:
        
        # iterate through all current paths extending them to new valid coordinates
        # saves to new dictionary of directions
        newDirections = {}

        # loop starts with every known path
        for currentCoords in Directions.keys():
            
            # loads map data at this point
            connections = Map.get(currentCoords)[0]
            explored    = Map.get(currentCoords)[1]

            if False in explored:
                return(Directions.get(currentCoords))
            
            # for loop will try and create a new path by extending in available directions
            # which are existant, already explored, and the where the new coordinate is on the map
            # but not added to the coordsMapped list (list of coordinates already on existing pathes)
            for i in range(4):
                if connections[i] and explored[i]:
                    newCoordinate = shift(currentCoords,i)
                    if newCoordinate in coordsMapped:
                        pass
                    elif newCoordinate in Map:
                        newDirections[newCoordinate] = Directions[currentCoords]+[i]
                        coordsMapped.append(newCoordinate)

        # replace directions dictionary with updated directions one step further        
        Directions = newDirections

        # checks for all routes being terminated before reaching a unopen street
        if len(Directions) == 0:
            searching = FALSE
            print("No Unexplored Street Found")
            return []
        
    
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


## Main Body used for testing
if __name__ == '__main__':

    FullMap = {\
        (0, 0):[[True, False, False, True], [True, True, True, True]], \
        (1, 0):[[True, True, False, True], [True, True, True, True]], \
        (2, 0):[[True, True, False, False], [True, True, True, True]], \
        (0, 1):[[True, False, True, False], [True, True, True, True]], \
        (1, 1):[[False, False, True, True], [True, True, True, True]], \
        (2, 1):[[True, True, True, False], [True, True, True, True]], \
        (0, 2):[[False, False, True, True], [True, True, True, True]], \
        (1, 2):[[True, True, False, True], [True, True, True, True]], \
        (2, 2):[[True, True, True, False], [True, True, True, True]], \
        (0, 3):[[True, False, False, True], [True, True, True, True]], \
        (1, 3):[[True, True, True, True], [True, True, True, True]], \
        (2, 3):[[False, True, True, False], [True, True, True, True]], \
        (0, 4):[[False, False, True, True], [True, True, True, True]], \
        (1, 4):[[False, True, True, False], [True, True, True, True]]}

    IncompleteMap = {\
        (0, 0):[[True, False, False, True], [True, True, True, True]], \
        (1, 0):[[True, True, False, True], [True, True, True, True]], \
        (2, 0):[[True, True, False, False], [True, True, True, True]], \
        (0, 1):[[True, False, True, False], [True, True, True, True]], \
        (1, 1):[[False, False, True, True], [True, True, True, True]], \
        (2, 1):[[True, True, True, False], [True, True, True, True]], \
        (0, 2):[[False, False, True, True], [True, True, True, True]], \
        (1, 2):[[True, True, False, True], [True, True, True, True]], \
        (2, 2):[[True, True, True, False], [True, True, True, True]], \
        (0, 3):[[True, True, False, True], [True, False, True, True]], \
        (1, 3):[[True, True, True, True], [True, True, True, True]], \
        (2, 3):[[False, True, True, False], [True, True, True, True]], \
        (0, 4):[[False, False, True, True], [True, True, True, True]], \
        (1, 4):[[False, True, True, False], [True, True, True, True]]}

    pointToPointDirections(FullMap,(0,4),(0,0))
    #print(nearestUnexploredDirections(IncompleteMap,(1,3)))

    