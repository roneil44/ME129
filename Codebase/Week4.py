## Use this file for the main codebase

# Imports

from ast import While
from sre_parse import State
from Motor import Motor
import time
from Sensor import Sensor

# Define the motor pins.
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

sen1pin =
sen2pin =
sen3pin =

MAX_PWM_VALUE = 254
PWM_FREQ = 1000

## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    sensors = Sensor("sensors", sen1pin, sen2pin, sen3pin)
    vel = .15
    w = 0
    edge = "c" #Set edge for sensor updates l, r or c
    
    try:
        while True:
            motors.setvel(vel, w)
            state = sensors.read()

            # Include if statements for different states should 
            # just change vel and w based on state
            if state == 0:
                #TODO
                pass
            elif state == 1:
                #TODO
                pass
            elif state == 2:
                #TODO
                pass
            elif state == 3:
                #TODO
                pass
            elif state == 4:
                #TODO
                pass
            elif state == 5:
                #TODO
                pass
            elif state == 6:
                #TODO
                pass
            elif state == 7:
                #TODO
                pass
                     
        


    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()