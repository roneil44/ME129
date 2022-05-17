import threading
from Motor import Motor
import time
from Sensor import Sensor
from Ultrasonic import Ultrasonic

#Define pins
MTR1_LEGA = 7
MTR1_LEGB = 8

MTR2_LEGA = 5
MTR2_LEGB = 6

sen_left_pin = 14
sen_mid_pin = 15
sen_right_pin = 18

ultra_left_echo = 16
ultra_left_trig = 13
ultra_mid_echo = 20
ultra_mid_trig = 19
ultra_right_echo = 21
ultra_right_trig = 26

if __name__ == "__main__":
    try:
        ULTRA_1 = Ultrasonic("ULTRA_1", ultra_left_echo, ultra_left_trig)
        ULTRA_2 = Ultrasonic("ULTRA_2", ultra_mid_echo, ultra_mid_trig)
        ULTRA_3 = Ultrasonic("ULTRA_3", ultra_right_echo, ultra_right_trig)

        while True:
            ULTRA_1.trigger()
            ULTRA_2.trigger()
            ULTRA_3.trigger()
            #wait 100 ms
            time.sleep(0.1)

            print("There is something " + str(ULTRA_1.dist) + "m away from sensor 1")
            print("There is something " + str(ULTRA_2.dist) + "m away from sensor 2")
            print("There is something " + str(ULTRA_3.dist) + "m away from sensor 3")

        
    except BaseException as ex:
        #exit out of the interrupt handlers
        ULTRA_1.cbfall.cancel()
        ULTRA_2.cbfall.cancel()
        ULTRA_3.cbfall.cancel()

        ULTRA_1.cbrise.cancel()
        ULTRA_2.cbrise.cancel()
        ULTRA_3.cbrise.cancel()
        
        print("Ending due to Exception: %s" % repr(ex))
