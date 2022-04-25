## Use this file for the main codebase

# Imports

from ast import While
from sre_parse import Pattern
from Motor import Motor
import time
from Sensor import Sensor

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

## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    sensors = Sensor("sensors", sen_left_pin, sen_mid_pin, sen_right_pin)
    vel = 0
    w = 0
    edge = "c" #Set edge for sensor updates l, r or c
    
    try:
        while True:
            motors.setvel(vel, w, 0)
            sensor_state = sensors.read()

            #Problem 1
            print("Left Sensor " + str(sensor_state[0]))
            print("Middle Sensor " + str(sensor_state[1]))
            print("Right Sensor " + str(sensor_state[2]) + "\n")
            time.sleep(0.25)            

            # Include if statements for different states should 
            # just change vel and w based on state
            # if state == 0:
            #     #TODO
            #     pass
            # elif state == 1:
            #     #TODO
            #     pass
            # elif state == 2:
            #     #TODO
            #     pass
            # elif state == 3:
            #     #TODO
            #     pass
            # elif state == 4:
            #     #TODO
            #     pass
            # elif state == 5:
            #     #TODO
            #     pass
            # elif state == 6:
            #     #TODO
            #     pass
            # elif state == 7:
            #     #TODO
            #     pass
                     
        


    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()