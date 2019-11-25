from abc import ABC, abstractclassmethod
import os
import random

if os.name == 'nt':
    pass
else:
    import Adafruit_DHT
    import RPi.GPIO as GPIO

class SensorBoard():
    def __init__(self):
        pass

    def sensor(self, sensor, *args):
        return sensor(*args)


class Board(SensorBoard):
    def __init__(self):
        pass

    def __enter__(self):
        GPIO.setmode(GPIO.BOARD)
        return self    
    
    def __exit__(self, *args): 
        GPIO.cleanup()

class BoardMock(SensorBoard):
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class Sensor(ABC):
    @abstractclassmethod
    def sense(self):
        pass


class TempSense(Sensor):
    def __init__(self, pin):
        self.pin = pin

    def __enter__(self):
        pass
        return self

    def __exit__(self, *args):
        pass

    def sense(self):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.pin)
        return (humidity, temperature)


class MotionSense(Sensor):
    def __init__(self, pin):
        self.pin = pin
    
    def __enter__(self):
        GPIO.setup(self.pin, GPIO.IN)
        return self
    
    def __exit__(self, *args):
        pass

    def sense(self):
        current_state = GPIO.input(self.pin)
        return current_state


class TempSenseMock(Sensor):
    def __init__(self, pin):
        self.pin = pin
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

    def sense(self):
        temp = random.randint(20, 51)
        hum = random.randint(20, 51)
        return temp, hum


class MotionSenseMock(Sensor):
    def __init__(self, pin):
        self.pin = pin
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def sense(self):
        return 1


