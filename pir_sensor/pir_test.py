import RPi.GPIO as GPIO
from time import sleep

pir_sensor = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_sensor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

current_state = 0

try:
    while True:
        current_state = GPIO.input(pir_sensor)
        print(current_state)
        sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
