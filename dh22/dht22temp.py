import Adafruit_DHT
import time

class TempSense():
	def __init__():
		pass

while(True):
	humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 17)

	humidity = round(humidity, 2)
	temperature = round(temperature, 2)

	if humidity is not None and temperature is not None:

		print('Temperatuur: {0:0.1f}*C'.format(temperature))
		print('Luchtvochtigheid: {0:0.1f}%'.format(humidity))

	else:
		print ('Geen data ontvangen')

	time.sleep(0.5)
