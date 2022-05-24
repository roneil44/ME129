import pigpio
import sys
import time

class Ultrasonic:
    trise = 0
    tfall = 0
    def __init__(self, name:str, echo:int, trig:int):
        self.name = name
        self.echo = echo
        self.trigger = trig

        self.dist = 1

        ############################################################
        # Prepare the GPIO connetion (to command the motors).
        print("Setting up the GPIO for Ultrasonic Sensor...")

        # Initialize the connection to the pigpio daemon (GPIO interface).
        self.io = pigpio.pi()
        if not self.io.connected:
            print("Unable to connection to pigpio daemon!")
            sys.exit(0)

        # Set up the two pins, echo as input and trigger as output
        self.io.set_mode(self.echo, pigpio.INPUT)
        self.io.set_mode(self.trigger, pigpio.OUTPUT)

        #want to access this from the outside to exit cleanly
        self.cbrise = self.io.callback(self.echo, pigpio.RISING_EDGE, self.rising)
        self.cbfall = self.io.callback(self.echo, pigpio.FALLING_EDGE, self.falling)
        print("GPIO ready...")
    
    #interrupt handler for rising edge
    def rising(self, gpio, newLevel, tick):
        self.trise = tick
        return
    
    #interrupt handler for falling edge, records distance in meters
    def falling(self, gpio, newLevel, tick):
        self.tfall = tick
        delta_tick = self.tfall - self.trise
        if delta_tick < 0: 
            delta_tick += (1 << 32)
        self.dist = 343/2 * delta_tick/1000000
        return

    def send_trigger(self):
        # Pull one (or all) trigger pins HIGH
        self.io.write(self.trigger, 1)

        # Hold for 10 microseconds.
        time.sleep(0.000010)

        # Pull the pins LOW again.
        self.io.write(self.trigger, 0)
        return

    def get_dist(self):
        return(self.dist)
