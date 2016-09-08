import logging
import sys
import time
from apidou import *

def main():
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

	adapter = raw_input("Quel type de peripherique BLE ? (entrez bled112 ou linux)\n")

	scan_result = APIdou.scan(adapter, timeout=5)
	for i in range(0, len(scan_result)):
		print i, ") Name :", scan_result[i]['name'], "/ Address: ", scan_result[i]['address']
		i += 1

	nb = raw_input("A quel periph se connecter ? ")
	if int(nb) not in range(0, len(scan_result)):
		print "Not a valid choice"
		sys.exit(0)
	try:
		apidou = APIdou(adapter, scan_result[int(nb)]['address'])
		apidou.connect()
	except pygatt.exceptions.NotConnectedError:
		print "Could not connect. Check if device is on (program will exit)"
		sys.exit(0)

	apidou.setVibration(True)
	time.sleep(0.1)
	apidou.setVibration(False)

	# apidou.setNotifyAccel(True)
	# while True:
	# 	print "Accel: ", apidou.accel

	apidou.disconnect()

if __name__ == '__main__':
	main()
