import logging
import sys
import time
from apidou import APIdou
import pygatt.exceptions

def main():
	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	backend = raw_input("Which BLE device are you using ? (entrez bled112 ou linux)\n")

	if backend not in {"bled112", "linux"}:
		print "Not a valid choice"
		return

	scan_result = APIdou.scan(backend, timeout=5)
	for i in range(0, len(scan_result)):
		print i, ") Name :", scan_result[i]['name'], "/ Address: ", scan_result[i]['address']
		i += 1

	nb = raw_input("A quel periph se connecter ? ")
	try:
		choice = int(nb)
	except ValueError:
		print "Please enter a number"
		return
	if choice not in range(0, len(scan_result)):
		print "Not a valid choice"
		return

	try:
		apidou = APIdou(adapter, scan_result[choice]['address'])
		apidou.connect()
	except pygatt.exceptions.NotConnectedError:
		print "Could not connect. Check if device is on (program will exit)"
		return

	apidou.setVibration(True)
	time.sleep(0.1)
	apidou.setVibration(False)

	apidou.disconnect()

if __name__ == '__main__':
	main()
