import os, pty, serial, termios
import threading
import struct

kill_thread = False
read_buffer = ""

class ComThread(threading.Thread):
	def __init__(self, out):
		threading.Thread.__init__(self)
		self.out = out

	def run(self):
		global kill_thread
		global read_buffer

		data = ""
		while kill_thread == False:
			data += os.read(self.out, 1)
			print data
			if data[-1] == "$":
				data = data[:-1]
				read_buffer = data
				data = ""


class COMSend():
	""" Fake serial port class"""

	def __init__(self):
		self.start()

	def start(self):
		""" Create the fake serial port """

		master, slave = pty.openpty()
		s_name = os.ttyname(slave)
		# Desactivation de l'echo sur le fake serial
		old_settings = termios.tcgetattr(master)
		new_settings = termios.tcgetattr(master)
		new_settings[3] = new_settings[3] & ~termios.ECHO
		termios.tcsetattr(master, termios.TCSADRAIN, new_settings)
		# make the sure the port is readable (if the script is launched as root)
		os.chmod(s_name, 0664)
		self.master = master
		self.slave = slave
		self.thread = ComThread(master)
		self.thread.daemon = True
		self.thread.start()
		print "Fake serial lance sur : " + s_name

	def send(self, msg):
		""" send a list of message strings to pd """
		try:
			os.write(self.master, msg)
		except Exception as e:
			print e
		# except:
			# print 'Could not send. Did you open a connection?'

	def send_packet(self, apidou):
		""" Format the string and send it to com port
			Sending everytime all the data is not pretty
			but makes coding on the other side easier
		"""
		packet = struct.pack("hhhhhhhB", apidou.touch, apidou.accel[0],apidou.accel[1],apidou.accel[2],\
											 apidou.gyro[0],apidou.gyro[1],apidou.gyro[2], 42)
		self.send(packet)

	def get_message(self):
		global read_buffer

		copy = read_buffer
		read_buffer = ""
		return copy

	def close(self):
		""" close the serial connection """
		global kill_thread
		os.close(self.master)
		os.close(self.slave)
		kill_thread = True