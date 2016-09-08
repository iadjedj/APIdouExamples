# coding: utf8
#
#			Python pour APIdou
# Code basé sur la librairie BluePy par IanHarvey
# 		https://github.com/IanHarvey/bluepy
#
# Installation :
# sudo apt-get install python-pip libglib2.0-dev
# sudo pip install bluepy
#
#
import struct
import time
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
	def __init__(self, apidouClass):
		btle.DefaultDelegate.__init__(self)
		self.apidou = apidouClass

	def handleNotification(self, handle, data):
		if len(data) == 8:
			self.apidou.updateData(data)

class APIdou():
	def __init__(self, addr):
		self.deviceAddr = addr
		self.initConnection()
		self.accel = 3 * [0]
		self.touch = 0

	def updateData(self, newData):
		data = struct.unpack("hhhh", newData)
		self.accel[0] = data[0]
		self.accel[1] = data[1]
		self.accel[2] = data[2]
		self.touch = data[3]

	def setVibration(self, state):
		if (state == True):
			self.client.writeCharacteristic(0x001e, struct.pack('b', 0x01))
		else:
			self.client.writeCharacteristic(0x001e, struct.pack('b', 0x00))

	def initConnection(self):
		self.client = btle.Peripheral(self.deviceAddr, btle.ADDR_TYPE_RANDOM, 0)
		self.client.setDelegate(DeviceDelegate(self))
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
	
	print "Peripheriques BLE a proximitée"
	scanner = btle.Scanner().withDelegate(ScanDelegate())
	devices = scanner.scan(5.0)
	nb = raw_input("A quel péripherique se connecter ? ")

	addr = scan_result[int(nb)].addr
	#addr = "c3:a0:f5:31:56:21"

	apidou = APIdou(addr)

	# Activer le vibreur pendant 150ms pour tester la connection
	apidou.setVibration(True)
	time.sleep(0.15)
	apidou.setVibration(False)

	while True:
		if apidou.waitForNotifications(10.0):
			print "Accel : ( x:", apidou.accel[0], "y:", apidou.accel[1], "z:", apidou.accel[2], ") Touch :", apidou.touch
			continue
		print "Reconnect..."
		apidou.disconnect()
		time.sleep(1.0)
		apidou.initConnection()