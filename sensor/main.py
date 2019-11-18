import os

from sensor import Board

if os.name == 'nt':
    from sensor import MotionSenseMock as MotionSense
    from sensor import TempSenseMock as TempSense
    from sensor import BoardMock as Board
else:
    from sensor import Board
    from sensor import TempSense
    from sensor import MotionSense

if __name__ == '__main__':
    with Board() as b:
        with b.sensor(MotionSense, 7) as m:
            
            print(m.sense())
        with b.sensor(TempSense, 17) as t:
            print(t.sense())


#    with MotionSense(7) as m:
#        print(m.sense())
#    
#    with TempSense(17) as t:
#        print(t.sense())
