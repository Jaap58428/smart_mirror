import RPi.GPIO as GPIO
from time import sleep

pir_sensor = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pir_sensor, GPIO.IN)

current_state = 0

try:
    print("Booting up PIR sensor...")
    sleep(15)
    print("PIR sensor ready")

    while True:
        current_state = GPIO.input(pir_sensor)
        print(current_state)
        sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
