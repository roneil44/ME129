# imports
from turtle import left
from typing import Optional
import pigpio
import sys
import time

# Define the motor pins.



class Motor:

    def __init__(self, name:str, MTR1_LEGA:int, MTR1_LEGB:int, MTR2_LEGA:int, MTR2_LEGB:int, MAX_PWM_VALUE:int, PWM_FREQ:int):
        self.name = name
        self.LEG1A = MTR1_LEGA
        self.LEG1B = MTR1_LEGB
        self.LEG2A = MTR2_LEGA
        self.LEG2B = MTR2_LEGB
        self.PWM = MAX_PWM_VALUE
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
        self.io.set_PWM_range(MTR1_LEGA, MAX_PWM_VALUE)
        self.io.set_PWM_range(MTR1_LEGB, MAX_PWM_VALUE)
        self.io.set_PWM_range(MTR2_LEGA, MAX_PWM_VALUE)
        self.io.set_PWM_range(MTR2_LEGB, MAX_PWM_VALUE)
        
        # Set the PWM frequency to 1000Hz.  You could try 500Hz or 2000Hz
        # to see whether there is a difference?
        self.io.set_PWM_frequency(MTR1_LEGA, PWM_FREQ)
        self.io.set_PWM_frequency(MTR1_LEGB, PWM_FREQ)
        self.io.set_PWM_frequency(MTR2_LEGA, PWM_FREQ)
        self.io.set_PWM_frequency(MTR2_LEGB, PWM_FREQ)

        # Clear all pins, just in case.
        self.io.set_PWM_dutycycle(MTR1_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR1_LEGB, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGA, 0)
        self.io.set_PWM_dutycycle(MTR2_LEGB, 0)

        print("GPIO ready...")

    def move(self, speed1:float, speed2:float, duration):
        #Detects if movement direction should be forward or backward and then calls the motor for movement
        # For our own benfit we could make this take a value beteen -100 to 100 or -1 to 1 if we don't want 
        # to have to worry about using the actual pwn values in the rest of the code.
        # Then run for the time duration given in seconds.
        # Note, out of bounds values will print a warning and set speed to 0
        
        #Convert to PWM
        s1 = speed1 * self.PWM
        s2 = speed2 * self.PWM

        if speed1 > 0 and speed1 <= 1 :
            self.io.set_PWM_dutycycle(self.LEG1A, s1)
            self.io.set_PWM_dutycycle(self.LEG1B,   0)
        elif speed1 < 0 and speed1 >= -1:
            self.io.set_PWM_dutycycle(self.LEG1A, 0)
            self.io.set_PWM_dutycycle(self.LEG1B, s1)
        else:
            self.io.set_PWM_dutycycle(self.LEG1A, 0)
            self.io.set_PWM_dutycycle(self.LEG1B, 0)
            if speed1 > 1 or speed1 < -1:
                print("Out of bounds speed1 value")

        if speed2 > 0 and speed2 <= 1 :
            self.io.set_PWM_dutycycle(self.LEG2A, s2)
            self.io.set_PWM_dutycycle(self.LEG2B,   0)
        elif speed2 < 0 and speed2 >= -1:
            self.io.set_PWM_dutycycle(self.LEG2A, 0)
            self.io.set_PWM_dutycycle(self.LEG2B, s2)
        else:
            self.io.set_PWM_dutycycle(self.LEG2A, 0)
            self.io.set_PWM_dutycycle(self.LEG2B, 0)
            if speed2 > 1 or speed2 < -1:
                print("Out of bounds speed2 value")

        time.sleep(duration)

    def stop(self, duration:Optional[float] = 0):
        # stops any motor movement without removing IO
        self.io.set_PWM_dutycycle(self.LEG1A, 0)
        self.io.set_PWM_dutycycle(self.LEG1B, 0)
        self.io.set_PWM_dutycycle(self.LEG2A, 0)
        self.io.set_PWM_dutycycle(self.LEG2B, 0)
        time.sleep(duration)

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
        self.io.set_PWM_dutycycle(self.LEGA, 0)
        self.io.set_PWM_dutycycle(self.LEGB, 0)

        # Also stop the interface.
        self.io.stop()
    
    def set(self, leftdutycycle:float, rightdutycycle:float):
        # positive value = going forward
        # negative value = going backward
        if abs(leftdutycycle) > 1.0 or abs(rightdutycycle) > 1.0:
            print('Make sure values are between -1.0 and +1.0')
            return

        leftPWMValue = MAX_PWM_VALUE * abs(leftdutycycle)
        rightPWMValue = MAX_PWM_VALUE * abs(rightdutycycle)
        if leftdutycycle < 0:
            #going backward, set MTR2_LEGB
            print("Moving left wheel backwards...")
            self.io.set_PWM_dutycycle(MTR2_LEGA, 0)
            self.io.set_PWM_dutycycle(MTR2_LEGB, leftPWMValue)
        else:
            #going forward, set MTR2_LEGA
            print("Moving left wheel forwards...")
            self.io.set_PWM_dutycycle(MTR2_LEGB, 0)
            self.io.set_PWM_dutycycle(MTR2_LEGA, leftPWMValue)
        if rightdutycycle <0:
            #going backward, set MTR1_LEGB
            print("Moving right wheel backwards...")
            self.io.set_PWM_dutycycle(MTR1_LEGA, 0)
            self.io.set_PWM_dutycycle(MTR1_LEGB, rightPWMValue)
            pass
        else:
            #going forward, set MTR1_LEGA
            print("Moving right wheel forwards...")
            self.io.set_PWM_dutycycle(MTR1_LEGB, 0)
            self.io.set_PWM_dutycycle(MTR1_LEGA, rightPWMValue)
        

