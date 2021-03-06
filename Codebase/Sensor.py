# imports
from turtle import left
from typing import Optional
import pigpio
import sys
import time



class Sensor:

    def __init__(self, name:str, io, sens1:int, sens2:int, sens3:int):
        self.name = name
        self.sens1 = sens1
        self.sens2 = sens2
        self.sens3 = sens3        

        ############################################################
        # Prepare the GPIO connetion (to command the motors).
        print("Setting up the GPIO...")

        # Initialize the connection to the pigpio daemon (GPIO interface).
        self.io = io
        if not self.io.connected:
            print("Unable to connection to pigpio daemon!")
            sys.exit(0)

        # Set up the four pins as input (taking in sensor input).
        self.io.set_mode(sens1, pigpio.INPUT)
        self.io.set_mode(sens2, pigpio.INPUT)
        self.io.set_mode(sens3, pigpio.INPUT)

        print("GPIO ready...")

    def read(self) -> int:
    # Reads sensor array and return list of values
        
        state1 = self.io.read(self.sens1)
        state2 = self.io.read(self.sens2)
        state3 = self.io.read(self.sens3)

        sensor_state = [state1,state2,state3]
        state = 4*sensor_state[0]+2*sensor_state[1]+sensor_state[2]
        
        return state
        
    