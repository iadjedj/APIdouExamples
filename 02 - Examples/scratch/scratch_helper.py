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

app = Flask("hue_helper_app")
apidou = ''

@app.route('/poll')
def poll():
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

	print msg
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
	"""
	Put some doc here
	"""
	logging.basicConfig(stream=sys.stdout, level=logging.ERROR)

	try:
		global apidou
		# Create an APIdou object using a BlueGiga adapter
		# and a given MAC address
		apidou = APIdou("linux", "CB:99:E8:46:1F:46")
		# Connect to this APIdou
		apidou.connect()

		# Make the APIdou vibrate for 100ms to check if connection is ok
		apidou.setVibration(True)
		time.sleep(0.1)
		apidou.setVibration(False)

		apidou.setNotifyAccel(True)
		apidou.setNotifyTouch(True)

		print "Connected to APIdou"
		print(" * Press Control + C to quit.")
		print "APIdou helper launched"
		app.run('0.0.0.0', port=1337)
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