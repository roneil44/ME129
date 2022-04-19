## Use this file for the main codebase

# Imports

from Motor import Motor
import time


SLOW_SPEED = 0.3
MID_SPEED = 0.6
FAST_SPEED = 0.9
SECONDS_RUN = 1
## Main Body

if __name__ == '__main__':
    try:
        # Robot execution code # 
        motor = Motor("pi")
        print('motor initialized')
        motor.set(SLOW_SPEED, SLOW_SPEED)
        time.sleep(SECONDS_RUN)
        motor.shutdown()
    except: 
       motor.shutdown() 
    pass 