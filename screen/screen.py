from itertools import count
from tkinter import *
from time import sleep
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

window = Tk()
window.geometry("600x400")
window.title("tkinter!")

lbl = Label(window, text="EMPTY", )
lbl.pack()

PIR_SENSOR = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_SENSOR, GPIO.IN)

print("Bootin device")
sleep(15)

while(True):
	s = 'no motion detected' if not GPIO.input(PIR_SENSOR) else 'MOTION DETECTED'

	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 17)

	if humidity is None or temperature is None:
		continue
	
	humidity = round(humidity, 2)
	temperature = round(temperature, 2)
		
	lbl.configure(text="Humidity = {}\t temperature = {}\t {}".format(humidity, temperature, s))
		
	window.update_idletasks()
	window.update()

