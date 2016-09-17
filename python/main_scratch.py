import logging
import sys
import time
from apidou import *
import socket
from array import array

sock = ''

def sendScratchCommand(cmd):
	global sock

	s = 'broadcast "' + cmd + '"'
	n = len(s)
	a = array('c')
	a.append(chr((n >> 24) & 0xFF))
	a.append(chr((n >> 16) & 0xFF))
	a.append(chr((n >>  8) & 0xFF))
	a.append(chr(n & 0xFF))
	print s
	sock.send(a.tostring() + s)

def main():
	"""
	Use this main as a template to build your python code
	"""

	global sock
	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	try:
		# Create an APIdou object using a BlueGiga adapter
		# and a given MAC address
		apidou = APIdou("bled112", "EC:12:AF:B3:20:F9")
		# Connect to this APIdou
		apidou.connect()

		# Make the APIdou vibrate for 100ms to check if connection is ok
		apidou.setVibration(True)
		time.sleep(0.1)
		apidou.setVibration(False)

		# Start the accelerometer and the touch sensor.
		# Warning : Without this, you will receive no data from APIdou
		apidou.setNotifyTouch(True)

		print("Connecting...")
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(("127.0.0.1", 42001))
		print("Connected!")

		while True:
			print apidou.touch
			if apidou.isTouched(APIdou.LEFT_FOOT):
				sendScratchCommand("pied_gauche")
			if apidou.isTouched(APIdou.RIGHT_FOOT):
				sendScratchCommand("pied_droit")
			if apidou.isTouched(APIdou.LEFT_HAND):
				sendScratchCommand("main_gauche")
			if apidou.isTouched(APIdou.RIGHT_HAND):
				sendScratchCommand("main_droite")
			if apidou.isTouched(APIdou.LEFT_EAR):
				sendScratchCommand("pied_gauche")
			if apidou.isTouched(APIdou.RIGHT_EAR):
				sendScratchCommand("pied_droit")
			if apidou.isTouched(APIdou.ANTENNA):
				sendScratchCommand("antenne")
			time.sleep(0.1)

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

