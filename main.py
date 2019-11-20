import datetime

with open('/home/pi/smart_mirror/smart_mirror.log', 'w') as f:
	f.write("Succesfull boot at {} \n".format( datetime.datetime.now()))

#	print ("Succesfull boot at", datetime.datetime.now())
