from itertools import count
from tkinter import *
from time import sleep
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

window = Tk()
window.geometry("600x400")
window.title("Smart mirror")

lbl = Label(window, text="EMPTY", )
lbl.pack()

PIR_SENSOR = 7

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIR_SENSOR, GPIO.IN)

print("Booting device...")
for i in reversed(range(15)):
	print("[*] {} [*]".format(i))
	sleep(1)

humidity = 0
temperature = 0
motion = 0

while(True):
	new_motion = GPIO.input(PIR_SENSOR)
	new_humidity, new_temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 17)
	
	new_humidity = round(new_humidity, 2)
	new_temperature = round(new_temperature, 2)
	if new_humidity == humidity and new_temperature == temperature and new_motion == motion:
		continue
	
	humidity = new_humidity
	temperature = new_temperature
	motion = new_motion

	s = 'no motion detected' if not motion else 'MOTION DETECTED'
	
	lbl.configure(text="Humidity = {}\n Temperature = {}\n Motion = {}".format(humidity, temperature, s))
		
	window.update_idletasks()
	window.update()

