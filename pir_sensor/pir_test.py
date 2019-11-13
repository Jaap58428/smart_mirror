import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

current_state = 0

for i in range(20):


    try:
        time.sleep(0.5)
	GPIO.setup(pir_sensor, GPIO.IN)
	    current_state = GPIO.input(i)
	    print(current_state, i)
	except KeyboardInterrupt:
	    pass

