import pygatt.backends
import struct

class APIdou():
	"""
		Python class for simplifying communication with APIdou
		Based on the PyGATT library (https://github.com/peplin/pygatt/)
	"""
	accel_uuid	= "aef95801-5027-41dd-a0ae-7b5f6045d4d3"
	gyro_uuid	= "aef95802-5027-41dd-a0ae-7b5f6045d4d3"
	touch_uuid	= "aef95803-5027-41dd-a0ae-7b5f6045d4d3"
	vib_uuid	= "aef95806-5027-41dd-a0ae-7b5f6045d4d3"

	LEFT_FOOT	= 2**0
	RIGHT_FOOT	= 2**1
	LEFT_HAND	= 2**2
	RIGHT_HAND	= 2**3
	LEFT_EAR	= 2**4
	RIGHT_EAR	= 2**5
	ANTENNA		= 2**6

	def __init__(self, backend, mac, hci_device='hci0'):
		""" Default constructor
				Arguments :
					backend : Can be "bled112" or "gatttool"
						- Use bled112 with the BLED112 USB Dongle from BlueGiga.
						PyGATT should autodetect the port
						- Use linux for any BLE adapter compatible with
						the Linux BLE command line interface
					mac : Your APIdou MAC address in the form :	01:23:45:67:89:AB
					hci_device (optionnal) : Let you specify another device name for
					the linux backend (hci0 by default)
		"""
		self.backend = backend
		self.address = mac
		self.accel = 3 * [0]
		self.gyro = 3 * [0]
		self.touch = 0
		self.hci = hci_device

	@staticmethod
	def scan(backend, timeout=5):
		""" (static method) Launch a BLE scan """
		if backend == "bled112":
			adapter = pygatt.backends.BGAPIBackend()
		elif backend == "linux":
			adapter = pygatt.backends.GATTToolBackend()
		else:
			print "Unkown backend (valid values are bled112 and linux)"
			return {0}
		adapter.start()
		scan_result = adapter.scan(timeout=timeout)
		adapter.stop()
		return scan_result

	def connect(self):
		""" Connect to APIdou with the correct backend """
		if self.backend == "bled112":
			self.adapter = pygatt.backends.BGAPIBackend()
			self.adapter.start()
			self.device = self.adapter.connect(self.address, addr_type=1)
			self.getHandles()
		elif self.backend == "linux":
			self.adapter = pygatt.backends.GATTToolBackend(hci_device=self.hci)
			self.adapter.start()
			self.device = self.adapter.connect(self.address, address_type='random')
			self.getHandles()
		else:
			print "Unkown backend (valid values are bled112 and linux)"

	def getHandles(self):
		"""	Retrieves and stores the handles for each characteristic.
		Not useful at the moment (except for the vib) but may be useful later
		because in pygatt, each read/write calls get_handle.
		Doing these operations by handles is a lot cleaner.
		You can also use these handles if you write your own notification
		callbacks to known wich characteristic has been notified.
		"""
		self.accel_handle	= self.device.get_handle(self.accel_uuid)
		self.gyro_handle	= self.device.get_handle(self.gyro_uuid)
		self.touch_handle	= self.device.get_handle(self.touch_uuid)
		self.vib_handle		= self.device.get_handle(self.vib_uuid)

	def disconnect(self):
		""" Stops the vibration motor, disconnect from APIdou
		and put the adapter in a clean state
		"""
		if hasattr(self, 'device'):
			self.setVibration(False)
			self.device.disconnect()
		self.adapter.stop()

	def accelNotificationCallback(self, handle, value):
		"""Default callback for the accelerometer """
		if len(value) == 6:
			self.accel = struct.unpack("hhh", value)

	def gyroNotificationCallback(self, handle, value):
		"""Default callback for the gyroscope """
		if len(value) == 6:
			self.gyro = struct.unpack("hhh", value)

	def touchNotificationCallback(self, handle, value):
		"""Default callback for the touch sensor """
		if len(value) == 1:
			self.touch = struct.unpack("B", value)[0]

	def __subscribe(self, uuid, callback):
		""" Subscribe to a specific characteristic and handle a little bug
		that can happen using the PyGATT BLED112 backend
		"""
		try:
			self.device.subscribe(uuid, callback)
		except pygatt.backends.bgapi.exceptions.ExpectedResponseTimeout:
			# sometimes the bled112 drops an answer to subscribe request
			# because the first notification comes before.
			pass

	def setNotifyAccel(self, state, callback=None):
		""" Activate/Deactivate notifications for the accelerometer 
		The optionnal callback parameters let you override the default 
		internal callback for this notification
		"""
		if state == True:
			if callback == None:
				self.__subscribe(self.accel_uuid, self.accelNotificationCallback)
			else:
				self.__subscribe(self.accel_uuid, callback)

		else:
			self.device.unsubscribe(self.accel_uuid)


	def setNotifyGyro(self, state, callback=None):
		""" Activate/Deactivate notifications for the gyroscope 
		The optionnal callback parameters let you override the default 
		internal callback for this notification
		"""
		if state == True:
			if callback == None:
				self.__subscribe(self.gyro_uuid, self.gyroNotificationCallback)
			else:
				self.__subscribe(self.gyro_uuid, callback)

		else:
			self.device.unsubscribe(self.gyro_uuid)

	def setNotifyTouch(self, state, callback=None):
		""" Activate/Deactivate notifications for the touch sensor
		The optionnal callback parameters let you override the default 
		internal callback for this notification
		"""
		if state == True:
			if callback == None:
				self.__subscribe(self.touch_uuid, self.touchNotificationCallback)
			else:
				self.__subscribe(self.touch_uuid, callback)

		else:
			self.device.unsubscribe(self.touch_uuid)

	def setVibration(self, state):
		""" Sets the vibration motor on or off
		A quick pulse of 0.1s is enough to be felt, remember that using
		the vibration motor	for	a long period of time greatly reduces
		battery life 
		"""
		if hasattr(self, 'vib_handle') == False:
			return
		if state == True:
			self.device.char_write_handle(self.vib_handle, bytearray([0x01]))
		else:
			self.device.char_write_handle(self.vib_handle, bytearray([0x00]))

	def isTouched(self, zones):
		""" Returns True if the specified zone is touched.
		You can also use binary operation to check multiple zones at the same time
		Examples :
		Check if the antenna is touched
		apidou.isTouched(APIdou.ANTENNA)
		Check if both arms are touched
		apidou.isTouched(APIdou.LEFT_HAND & APIdou.RIGHT_HAND)
		Check if one of the ears is touched
		apidou.isTouched(APIdou.LEFT_EAR | APIdou.RIGHT_EAR)

		"""
		if (self.touch & zones) != 0:
			return True
		else:
			return False