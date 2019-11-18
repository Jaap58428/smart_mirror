import os
if os.name == 'nt':
    from sensor import MotionSenseMock as MotionSense
    from sensor import TempSenseMock as TempSense
else:
    from sensor import TempSense
    from sensor import MotionSense

if __name__ == '__main__':
    with MotionSense(7) as m:
        print(m.sense())
    
    with TempSense(17) as t:
        print(t.sense())
