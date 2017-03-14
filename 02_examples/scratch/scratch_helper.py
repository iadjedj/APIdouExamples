#! /usr/bin/python

# Scratch APIdou Helper app
# ----------------------
# Based on the work of Chris Proctor
# Distributed under the MIT license.
# Project homepage: http://www.apidou.fr

from flask import Flask
from apidou import *
import logging
import pygatt.exceptions
import sys
import time
import argparse

app = Flask("hue_helper_app")
apidou = ''

def bold(s):
	return '\033[1m' + str(s) + '\033[0m'

def reconnect():
	try:
		apidou.adapter.stop()
		apidou.connect()
		apidou.setNotifyAccel(True)
		apidou.setNotifyTouch(True)
	except Exception as e:
		print "Exception during reconnect", e
		pass

@app.route('/poll')
def poll():
	try:
		rssi = apidou.device.get_rssi()
		if rssi == 0:
			reconnect()
			return '_problem The device is disconnected. Relaunch the helper script'
	except pygatt.exceptions.NotConnectedError:
		reconnect()
		return '_problem The device is disconnected. Relaunch the helper script'

	msg = "touch/pied_gauche "
	msg += "true" if apidou.isTouched(APIdou.LEFT_FOOT) else "false"

	msg += "\ntouch/pied_droit "
	msg += "true" if apidou.isTouched(APIdou.RIGHT_FOOT) else "false"

	msg += "\ntouch/main_gauche "
	msg += "true" if apidou.isTouched(APIdou.LEFT_HAND) else "false"

	msg += "\ntouch/main_droite "
	msg += "true" if apidou.isTouched(APIdou.RIGHT_HAND) else "false"

	msg += "\ntouch/oreille_gauche "
	msg += "true" if apidou.isTouched(APIdou.LEFT_EAR) else "false"

	msg += "\ntouch/oreille_droite "
	msg += "true" if apidou.isTouched(APIdou.RIGHT_EAR) else "false"

	msg += "\ntouch/antenne "
	msg += "true" if apidou.isTouched(APIdou.ANTENNA) else "false"

	pos = apidou.getPosition()

	msg += "\nposition/sur_le_dos "
	msg += "true" if pos == APIdou.APIdouPositions.ON_THE_BACK else "false"

	msg += "\nposition/sur_le_ventre "
	msg += "true" if pos == APIdou.APIdouPositions.FACING_DOWN else "false"

	msg += "\nposition/debout "
	msg += "true" if pos == APIdou.APIdouPositions.STANDING else "false"

	msg += "\nposition/la_tete_en_bas "
	msg += "true" if pos == APIdou.APIdouPositions.UPSIDE_DOWN else "false"

	msg += "\nposition/sur_la_gauche "
	msg += "true" if pos == APIdou.APIdouPositions.ON_THE_LEFT else "false"

	msg += "\nposition/sur_la_droite "
	msg += "true" if pos == APIdou.APIdouPositions.ON_THE_RIGHT else "false"

	msg += "\n"

	if apidou.touch == 127:
		msg += "calin true\n"
	else:
		msg += "calin false\n"

	if apidou.isShaken():
		msg += "shake true\n"
	else:
		msg += "shake false\n"

	return msg

@app.route('/vibrate/<int:length>')
def vibrate(length):
	apidou.setVibration(True)
	time.sleep(float(length) / 1000)
	apidou.setVibration(False)
	return "OK"

@app.route('/reset_all')
def reset_all():
	apidou.setVibration(False)
	return "OK"

@app.route('/crossdomain.xml')
def cross_domain_check():
	return """
<cross-domain-policy>
	<allow-access-from domain="*" to-ports="1337"/>
</cross-domain-policy>
"""

def main():
	""" Helper to communicate with Scratch 2.0 (offline version)
	This code uses Flask to create a small local HTTP server on port 1337,
	it implements the Scratch HTTP procotol (more info on :
	https://wiki.scratch.mit.edu/w/images/ExtensionsDoc.HTTP-9-11.pdf )
	"""
	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	print bold("==========================================")
	print bold("            APIdou > Scratch              ")
	print bold("==========================================")
	print "Launching BLE scan, please wait..."
	scan_result = APIdou.scan("bled112", timeout=5)

	i = 1
	for dev in scan_result:
		print bold(i), ") Name:", bold(dev['name'] or "(No Name)")
		i += 1
	nb = raw_input("Please enter the number corresponding to your APIdou : ")

	try:
		choice = int(nb) - 1
	except ValueError:
		print "Please enter a number"
		return
	if choice < 0 or choice > len(scan_result) - 1:
		print "Not a valid choice"
		return
	else:
		print "\nConnecting to", bold(scan_result[choice]['name'])

	try:
		global apidou

		apidou = APIdou("bled112", scan_result[choice]['address'])
		apidou.connect()
		print "Connected to", bold(scan_result[choice]['name'])

		# Make the APIdou vibrate for 100ms to check if connection is ok
		apidou.setVibration(True)
		time.sleep(0.1)
		apidou.setVibration(False)

		apidou.setNotifyAccel(True)
		apidou.setNotifyTouch(True)

		print "HTTP extension launched"
		print "Press Control + C to quit"
		app.run('0.0.0.0', port=1337)
	# except pygatt.exceptions.NotConnectedError:
		# print "Could not connect. Check if device is on (program will exit)"
	except KeyboardInterrupt:
		print "\nCtrl-C pressed. Goodbye!"
	except Exception as e:
		print e
	finally:
		apidou.disconnect()

if __name__ == '__main__':
	main()
