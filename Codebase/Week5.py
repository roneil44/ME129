## Use this file for the main codebase

# Imports

from ast import While
from sre_parse import Pattern
from turtle import right
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
    edge = "c" #Set edge for sensor updates l, r or c

    
    try:
        
            

        def drive():
            #returns 0 at end
            #returns 1 at intersection
            #bot is centered on end criteria when block ends
            exit_condition = -1

            while(exit_condition == -1):
                sensor_state = sensors.read()

                #sensor load
                state = 4*sensor_state[0]+2*sensor_state[1]+sensor_state[2]

                if state == 0:
                    exit_condition = 0

                elif state == 1: #Drifted far left
                    motors.setvel(0.1, 100, 0.01)
                    edge = 'l'


                elif state == 2: #Bot Centered
                    motors.setvel(0.35, 0, 0.01)
                    edge = 'c'


                elif state == 3: #Drifted Left
                    motors.setvel(0.1, 50, 0.01)
                    edge = 'l'


                elif state == 4: #Drfted far right
                    motors.setvel(0.1, -100, 0.01)
                    edge = 'r'


                elif state == 5: #Split in the tape
                    pass


                elif state == 6: #Drifted Right
                    motors.setvel(0.1, -50, 0.01)
                    edge = 'r'

                #intersection found
                elif state == 7:  #Thick part of tape
                    exit_condition = 1

                print(edge)
                print(state)

            motors.stop()
            motors.movedist(0.127)
            return(exit_condition)
            


    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()