# imports

class Motor:

    def __init__(self, name:str):
        self.name = name

    def move(self, speed:int):
        #Detects if movement direction should be forward or backward and then calls the motor for movement
        # For our own beenfit we could make this take a value beteen -100 to 100 or -1 to 1 if we don't want 
        # to have to worry about using the actual pwn values in the rest of the code.
        pass

    def stop(self):
        # stops any motor movement
        pass

    def movedist(self, dist:float):
        #Might want a method that takes in a distance rather than speed input
        pass
    
