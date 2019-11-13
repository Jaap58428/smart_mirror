import RPi.GPIO as GPIO
import time

pir_sensor = 11

GPIO.setmode(GPIO.BOARD)

GPIO.setup(pir_sensor, GPIO.IN)

current_state = 0
try:
    while True:
        time.sleep(0.1)
        current_state = GPIO.input(pir_sensor)
        if current_state == 1:
            print("Motion detected!")
        else:
            print("No motion detected :(")
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
