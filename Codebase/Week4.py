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
        while True:
            sensor_state = sensors.read()

            # #Problem 2
            # print("Left Sensor " + str(sensor_state[0]))
            # print("Middle Sensor " + str(sensor_state[1]))
            # print("Right Sensor " + str(sensor_state[2]) + "\n")
            # time.sleep(0.25)            

            #Problem 3 + 4
            state = 4*sensor_state[0]+2*sensor_state[1]+sensor_state[2]

            #Include if statements for different states should 
            #just change vel and w based on state
            if state == 0 and edge == 'c': #Past End
                left = 0.3
                rigt = 0.9
                while True:
                    motors.move(left, rigt, 0.05)
                    left += 0.001
                    if left >= 0.9:
                        left =0.9
                    print(left)
                    sensor_state = sensors.read()
                    state = 4*sensor_state[0]+2*sensor_state[1]+sensor_state[2]
                    if state != 0:
                        break
            elif state == 0 and edge == 'l': #drifted off left edge
                motors.setvel(0, 200, 0.01)
            elif state == 0 and edge == 'r': #drifted off right edge
                motors.setvel(0, -200, 0.01)
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
            elif state == 7:  #Thick part of tape
                if edge == 'r':
                    motors.setvel(0, -200, 0.01)
                elif edge == 'l':
                    motors.setvel(0, 200, 0.01)

                pass            
            else:
                motors.stop() #haven't addressed this yet

            print(edge)
            print(state)

    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()