# imports
from turtle import left
import pigpio
import sys
import time

# Define the motor pins.
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

MAX_PWM_VALUE = 255

class Motor:

    def __init__(self, name:str):
        self.name = name
        ############################################################
        # Prepare the GPIO connetion (to command the motors).
        print("Setting up the GPIO...")

        # Initialize the connection to the pigpio daemon (GPIO interface).
        self.io = pigpio.pi()
        if not self.io.connected:
            print("Unable to connection to pigpio daemon!")
            sys.exit(0)

        # Set up the four pins as output (commanding the motors).
        self.io.set_mode(MTR1_LEGA, pigpio.OUTPUT)
        self.io.set_mode(MTR1_LEGB, pigpio.OUTPUT)
        self.io.set_mode(MTR2_LEGA, pigpio.OUTPUT)
        self.io.set_mode(MTR2_LEGB, pigpio.OUTPUT)

        # Prepare the PWM.  The range gives the maximum value for 100%
        # duty cycle, using integer commands (1 up to max).
        self.io.set_PWM_range(MTR1_LEGA, 255)
        self.io.set_PWM_range(MTR1_LEGB, 255)
        self.io.set_PWM_range(MTR2_LEGA, 255)
        self.io.set_PWM_range(MTR2_LEGB, 255)
        
        # Set the PWM frequency to 1000Hz.  You could try 500Hz or 2000Hz
        # to see whether there is a difference?
        self.io.set_PWM_frequency(MTR1_LEGA, 1000)
        self.io.set_PWM_frequency(MTR1_LEGB, 1000)
        self.io.set_PWM_frequency(MTR2_LEGA, 1000)
        self.io.set_PWM_frequency(MTR2_LEGB, 1000)

        # Clear all pins, just in case.
        self.io.set_PWM_dutycycle(MTR1_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR1_LEGB, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGB, 0)

        print("GPIO ready...")

    def move(self, speed:int):
        #Detects if movement direction should be forward or backward and then calls the motor for movement
        # For our own benfit we could make this take a value beteen -100 to 100 or -1 to 1 if we don't want 
        # to have to worry about using the actual pwn values in the rest of the code.
        pass

    def stop(self):
        # stops any motor movement
        pass

    def movedist(self, dist:float):
        #Might want a method that takes in a distance rather than speed input
        pass
    
    def shutdown(self):
        ############################################################
        # Turn Off.
        # Note the PWM still stay at the last commanded value.  So you
        # want to be sure to set to zero before the program closes.  else
        # your robot will run away...
        print("Turning off...")

        # Clear the PINs (commands).
        self.io.set_PWM_dutycycle(MTR1_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR1_LEGB, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGB, 0)
        
        # Also stop the interface.
        self.io.stop()
        pass
    
    def set(self, leftdutycycle:float, rightdutycycle:float):
        # positive value = going forward
        # negative value = going backward
        resolution = 1.0/MAX_PWM_VALUE
        leftPWMValue = resolution * abs(leftdutycycle)
        rightPWMValue = resolution * abs(rightdutycycle)
        if leftdutycycle < 0:
            #going backward, set MTR2_LEGB
            self.io.set_PWM_dutycycle(MTR2_LEGA, 0)
            self.io.set_PWM_dutycycle(MTR2_LEGB, leftPWMValue)
        else:
            #going forward, set MTR2_LEGA
            self.io.set_PWM_dutycycle(MTR2_LEGB, 0)
            self.io.set_PWM_dutycycle(MTR2_LEGA, leftPWMValue)
        if rightdutycycle <0:
            #going backward, set MTR1_LEGB
            self.io.set_PWM_dutycycle(MTR1_LEGA, 0)
            self.io.set_PWM_dutycycle(MTR1_LEGB, rightPWMValue)
            pass
        else:
            #going forward, set MTR1_LEGA
            self.io.set_PWM_dutycycle(MTR1_LEGB, 0)
            self.io.set_PWM_dutycycle(MTR1_LEGA, rightPWMValue)
        pass

