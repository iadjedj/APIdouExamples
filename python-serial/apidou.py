# coding: utf8
#
#			Redirection Serial pour APIdou
# Code basé sur la librairie BluePy par IanHarvey
# 		https://github.com/IanHarvey/bluepy
#
# Installation :
# sudo apt-get install python-pip libglib2.0-dev
# sudo pip install bluepy
#
#
import struct
import os, pty, serial
import sys, termios, time
import select
from bluepy import btle
from bluepy.btle import Scanner, DefaultDelegate

scan_result = []

class ScanDelegate(btle.DefaultDelegate):
	def __init__(self):
		self.nb_devices = 0
		btle.DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			scan_result.insert(self.nb_devices, dev)
			print self.nb_devices, ") Name :", dev.getValueText(9), "\tAddress:", dev.addr
			self.nb_devices += 1

class DeviceDelegate(btle.DefaultDelegate):
	def __init__(self, output):
		btle.DefaultDelegate.__init__(self)
		self.master = output

	def handleNotification(self, handle, data):
		# Redirection directe de la characteristique vers le fake serial
		if len(data) == 8:
			os.write(self.master, data)

class APIdou():
	def __init__(self, addr):
		self.deviceAddr = addr
		self.initConnection()

	def setVibration(self, state):
		if (state == True):
			self.client.writeCharacteristic(0x001e, struct.pack('b', 0x01))
		else:
			self.client.writeCharacteristic(0x001e, struct.pack('b', 0x00))

	def initConnection(self):
		self.client = btle.Peripheral(self.deviceAddr, btle.ADDR_TYPE_RANDOM, 0)
		self.client.setDelegate(DeviceDelegate(master))
		try:
			# Activation des notifications pour la characteristique
			self.client.writeCharacteristic(0x0013, struct.pack('bb', 0x01, 0x00))
		except BTLEException as e:
			print e

	def disconnect(self):
		self.client.disconnect()

	def waitForNotifications(self, time):
		try:
			if self.client.waitForNotifications(time):
				return True
			pass
		except btle.BTLEException as e:
			print e
			print "Device disconnected..."
		return False

if __name__ == '__main__':
	# Scan des peripheriques BLE a portée
	# Une fois l'addresse obtenue, 
	# il est possible de commenter cette section et de directement attribuer à "addr" l'addresse de votre APIdou
	
#	print "Peripheriques BLE a proximitée"
#	scanner = btle.Scanner().withDelegate(ScanDelegate())
#	devices = scanner.scan(5.0)
#	nb = raw_input("A quel péripherique se connecter ? ")

	#addr = scan_result[int(nb)].addr
	addr = "c3:a0:f5:31:56:21"

	# Creation du fake serial
	master, slave = pty.openpty()
	s_name = os.ttyname(slave)
	# Désactivation de l'echo sur le fake serial
	old_settings = termios.tcgetattr(master)
	new_settings = termios.tcgetattr(master)
	new_settings[3] = new_settings[3] & ~termios.ECHO
	termios.tcsetattr(master, termios.TCSADRAIN, new_settings)
	os.chmod(s_name, 0664)
	print "Fake serial lancé sur : " + s_name

	apidou = APIdou(addr)

	# Activer le vibreur pendant 150ms pour tester la connection
	apidou.setVibration(True)
	time.sleep(0.15)
	apidou.setVibration(False)

	q = select.poll()
	q.register(master, select.POLLIN)
	while True:
		# Read non bloquant sur le fake serial pour vérifier si l'état du vibreur doit changer
		l = q.poll(0)
		if not l:
			pass
		else:
			s = os.read(master, 10)
			if (s == "1"):
				apidou.setVibration(True)
			else:
				apidou.setVibration(False)
		if apidou.waitForNotifications(10.0):
			continue
		print "Reconnect..."
		apidou.disconnect()
		time.sleep(1.0)
		apidou.initConnection()