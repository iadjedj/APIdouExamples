import logging
import sys
import time
import argparse
from apidou import APIdou
from pdsend import *
if sys.platform.startswith('linux'):
	from comsend import *
import pygatt.backends

compt = 0
start_time = 0
apidou = ''

def APIdouCallback(handle, value):
	global apidou

	if handle == apidou.accel_handle:
		accel = struct.unpack("hhh", value)
		print "ACCEL", accel
	elif handle == apidou.gyro_handle:
		gyro = struct.unpack("hhh", value)
		print "GYRO", gyro
	elif handle == apidou.touch_handle:
		touch = struct.unpack("B", value)
		print "TOUCH", touch[0]

def handleMessage(device, message):
	if message == "1":
		device.setVibration(True)
		print "Vibration On"
	elif message == "0":
		device.setVibration(False)
		print "Vibration Off"
	else:
		print "Received an unknown message on socket"

def handleOutput(device, output, is_tcp):
	if is_tcp == True:
		# TODO : Implement a way to check which notification
		# is enabled and only send these ones
		output.send_packet(1, device.accel)
		output.send_packet(2, device.gyro)
		output.send_packet(3, {device.touch})
	else:
		output.send_packet(device)

	tmp = output.get_message()
	if tmp != "":
			handleMessage(device, tmp)

def main():
	global apidou

	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	parser = argparse.ArgumentParser()
	parser.add_argument('-type', '-t', required=True, choices=['bled112', 'linux'] ,\
		help='Are you using a BLED112 or regular BLE Adapter on Linux ?')
	parser.add_argument('-addr', '-a', required=True, \
		help='MAC address of your APIdou, e.g. 00:07:80:02:F2:F2')
	# To implement
	parser.add_argument('-tcp', required=False, \
		help='Activate a forward to TCP (port 3000)', action='store_true')
	parser.add_argument('-com', required=False, \
		help='Activate a forward to a COM port', action='store_true') 
	args = parser.parse_args()

	if args.tcp:
		output = PdSend()
	elif args.com:
		if sys.platform.startswith('linux'):
			output = COMSend()
		else:
			print "Serial redirection only works on Linux"
			return

	try:
		apidou = APIdou(args.type, args.addr)
		apidou.connect()

		apidou.setNotifyAccel(True)
		# apidou.setNotifyGyro(True)
		apidou.setNotifyTouch(True)
		print "Connected"
		while True:
			if apidou.isTouched(APIdou.ANTENNA):
				print "The antenna is touched"
			# print "Accel: ", apidou.accel
			# print "Gyro: ", apidou.gyro
			# print "touch: ", apidou.touch
			if args.tcp or args.com:
				handleOutput(apidou, output, args.tcp)
			time.sleep(0.01)

	except pygatt.exceptions.NotConnectedError:
		print "Could not connect. Check if device is on (program will exit)"
	except KeyboardInterrupt:
		print "\nCtrl-C pressed. Goodbye!"
	finally:
		apidou.disconnect()
		if args.tcp or args.com:
			output.close()

if __name__ == '__main__':
	main()

