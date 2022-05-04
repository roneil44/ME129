import config

class Intersection:
    # Initialize - create new intersection at (long, let)
    def __init__(self, long, lat):
        # Save the parameters.
        self.long = long
        self.lat = lat
        # Status of streets at the intersection, in NWSE directions.
        self.streets = [config.UNKNOWN, config.UNKNOWN, config.UNKNOWN, config.UNKNOWN]
        # Direction to head from this intersection in planned move.
        self.headingToTarget = None
        # You are welcome to implement an arbitrary number of
        # "neighbors" to more directly match a general graph.
        # But the above should be sufficient for a regular grid.
        # Add this to the global list of intersections to make it searchable.
        global intersections
        if intersections(long, lat) is not None:
            raise Exception("Duplicate intersection at (%2d,%2d)" % (long,lat))
        intersections.append(self)

    # Print format.
    def __repr__(self):
        return ("(%2d, %2d) N:%s W:%s S:%s E:%s - head %s\n" %
        (self.long, self.lat, self.streets[0],
        self.streets[1], self.streets[2], self.streets[3],
        config.HEADING[self.headingToTarget]))

