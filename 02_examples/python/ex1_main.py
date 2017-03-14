import logging
import sys
import time
from apidou import APIdou
import pygatt.exceptions

MY_APIDOU = "CB:99:E8:46:1F:46"

def main():
	"""
	Use this main as a template to build your python code
	"""
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

	try:
		# Create an APIdou object using a BlueGiga adapter
		# and a given MAC address
		apidou = APIdou("linux", MY_APIDOU)
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

			if apidou.getPosition() == APIdou.UPSIDE_DOWN:
				apidou.setVibration(True)
				time.sleep(0.1)
				apidou.setVibration(False)
			time.sleep(0.01)

	except pygatt.exceptions.NotConnectedError:
		print "Could not connect. Check if device is on (program will exit)"
	except KeyboardInterrupt:
		print "\nCtrl-C pressed. Goodbye!"
	except Exception as e:
		print e
	finally:
		apidou.disconnect()

if __name__ == '__main__':
	main()

