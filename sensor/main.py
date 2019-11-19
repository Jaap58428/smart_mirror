import os

if os.name == 'nt':
    from sensor import MotionSenseMock as MotionSense
    from sensor import TempSenseMock as TempSense
    from sensor import BoardMock as Board
else:
    from sensor import Board
    from sensor import TempSense
    from sensor import MotionSense

if __name__ == '__main__':
    with Board() as b, MotionSense(7) as m, TempSense(17) as t:
        print(m.sense())
        print(t.sense())
