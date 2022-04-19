## Use this file for the main codebase

# Imports

from Motor import Motor
import time
import pigpio
import sys

# Define the motor pins.
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

MAX_PWM_VALUE = 255
PWM_FREQ = 1000

## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    
    
    try:
        print("\nProblem 3.A")
        time.sleep(2)

        Lmotor.move(.5, 1)
        Rmotor.move(.5, 1)




    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    Lmotor.shutdown()
    Rmotor.shutdown()
