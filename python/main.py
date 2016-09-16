import logging
import sys
import time
from apidou import *


def main():
	"""
	Use this main as a template to build your python code
	"""
	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	try:
		# Create an APIdou object using a BlueGiga adapter
		# and a given MAC address
		apidou = APIdou("bled112", "E6:A4:7B:AB:A9:2D")
		# Connect to this APIdou
		apidou.connect()

		# Make the APIdou vibrate for 100ms to check if connection is ok
		apidou.setVibration(True)
		time.sleep(0.1)
		apidou.setVibration(False)

		# Start the accelerometer and the touch sensor.
		# Warning : Without this, you will receive no data from APIdou
		apidou.setNotifyAccel(True)
		apidou.setNotifyTouch(True)

		print "Connected"
		while True:
			if apidou.isTouched(APIdou.ANTENNA):
				print "The antenna is touched"
			print "Accel: ", apidou.accel
			time.sleep(0.01)

	except pygatt.exceptions.NotConnectedError:
		print "Could not connect. Check if device is on (program will exit)"
	except KeyboardInterrupt:
		print "\nCtrl-C pressed. Goodbye!"
	finally:
		apidou.disconnect()

if __name__ == '__main__':
	main()

