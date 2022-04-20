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

        #################################################################
        # print("\nProblem 3.A")
        # time.sleep(2)
        # motors.move(.5, .5, 2)
        # motors.stop()

        # time.sleep(2)
        # motors.move(.75, .75, 2)
        # motors.stop()


        #################################################################
        # print("\nProbelm 3.B")
        # time.sleep(2)
        # print("Driving Forward...")
        # motors.move(.67,.67,1)

        # print("Dwell...")
        # motors.stop(1)

        # print("Turn 180...")
        # motors.move(.607, -.607, 1)

        # print("Dwell...")
        # motors.stop(1)

        # print("Driving Forward...")
        # motors.move(.67, .67, 1)

        # print("Dwell...")
        # motors.stop(1)

        # print("Turn 180...")
        # motors.move(.607, -.607, 1)

        # print("Stop")
        # motors.stop(1)

        

        #################################################################
        # print("Problem 5")

        # motors.move(0.5,-0.5, 1.85)
        # motors.stop()


        #################################################################
        # print("Problem 6")
        # motors.setspin(200,"l",1)
        # motors.stop()

        # print("Problem 7")
        # print("Triangle")
        # motors.movedist(.2)
        # motors.angle(120)
        # motors.movedist(.2)
        # motors.angle(120)
        # motors.movedist(.2)
        # motors.stop(8)

        # print("Square")
        # motors.movedist(.2)
        # motors.angle(90)
        # motors.movedist(.2)
        # motors.angle(90)
        # motors.movedist(.2)
        # motors.angle(90)
        # motors.movedist(.2)
        

        print("Problem 8")
        print("circle")
        motors.setvel(.19635, 3.1415, 2)



    except BaseException as ex:
        print("Ending due to Exception: %s" % repr(ex))

    motors.shutdown()
