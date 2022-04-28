## Use this file for the main codebase

# Imports

from Motor import Motor
import time



## Main Body

if __name__ == '__main__':
    try:
        # Robot execution code # 
        motor = Motor("pi")
        print('motor initialized')
        motor.set(-0.4, -0.4)
        time.sleep(1)
        motor.shutdown()
    except: 
       motor.shutdown() 
    pass 