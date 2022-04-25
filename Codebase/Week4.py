## Use this file for the main codebase

# Imports

from Motor import Motor
import time

# Define the motor pins.
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

MAX_PWM_VALUE = 254
PWM_FREQ = 1000

## Main Body

if __name__ == '__main__':
    # Initialize mottos

    motors = Motor("motors", MTR1_LEGA, MTR1_LEGB, MTR2_LEGA, MTR2_LEGB, MAX_PWM_VALUE, PWM_FREQ)
    
    
    try:
        motors.angle(270)
        motors.sleep


    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()


def readsensors(elf):
