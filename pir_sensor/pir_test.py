import RPi.GPIO as GPIO
import time

pir_sensor = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

current_state = 0

try:
    while True:
        time.sleep(0.2)
        current_state = GPIO.input(pir_sensor)
        print(current_state)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()