# Global Constants:
# Headings
NORTH = 0
WEST = 1
SOUTH = 2
EAST = 3
HEADING = {NORTH: "North", WEST:"West", SOUTH:"South",
EAST:"East", None:"None"} # For printing

# Street status
UNKNOWN = "Unknown"
NOSTREET = "NoStreet"
UNEXPLORED = "Unexplored"
CONNECTED = "Connected"

# Global Variables:
intersections = [] # List of intersections
lastintersecion = None # Last intersection visited
long = 0 # Current east/west coordinate
lat = -1 # Current north/south coordinate
heading = NORTH # Current heading