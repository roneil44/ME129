## Use this file for the main codebase

# Imports

from Motor import Motor



## Main Body

if __name__ == '__main__':
    try:
        # Robot execution code # 
        motor = Motor()
        print('moto initialized"')
        #move left wheel forward
        motor.set(0.2, 0)
        motor.shutdown()
    except: 
       motor.shutdown() 
    pass 