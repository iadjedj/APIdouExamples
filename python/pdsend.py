import socket
import threading

kill_thread = False
read_buffer = ""

class SocketThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		global kill_thread
		global read_buffer

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create ipv4 socket
		self.socket.bind(('127.0.0.1', 3001))
		print "Listening to puredata on port 3001"
		self.socket.listen(1)
		self.sock, addr = self.socket.accept()
		data = ""
		print "Got an answer from PD"
		while kill_thread == False:
			data += self.sock.recv(1)
			if data[-1] == ";":
				data = data[:-1]
				data = data[1:]
				# print "SocketThread: Packet received :", data
				read_buffer = data
				data = ""


class PdSend():
	""" Simple socket wrapper to talk FUDI with PD """
	pdhost = 'localhost'
	sport = 3000
	pd = '' # the socket object will live here

	def __init__(self):
		self.connect()

	def connect(self):
		""" make a connection to pd """
		print 'Connecting to PD'
		try:
			self.pd = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create ipv4 socket
			self.pd.connect((self.pdhost, self.sport)) # make the connection
			# self.pd.settimeout(1)
			print 'Sending to PD on port ' + str(self.sport)
			self.thread = SocketThread()
			self.thread.daemon = True
			self.thread.start()
		except socket.error:
			print 'Connection failed - open PD with [netreceive ' + str(self.sport) + '] at least!'

	def send(self, msg):
		""" send a list of message strings to pd """
		try:
			self.pd.send(str(msg) + ';')
		except:
			print 'Could not send. Did you open a connection?'
			pass

	def send_packet(self, index, data):
		""" The APIdou way of sending data to pd
			ex : "1 x y z;" for the accelerometer
			The backslash is here to escape the space
		"""
		msg = str(index)
		for d in data:
			msg += "\ " + str(d)
		self.send(msg)

	def get_message(self):
		global read_buffer

		copy = read_buffer
		read_buffer = ""
		return copy

	def close(self):
		""" close the socket connection """
		global kill_thread
		print 'Closing connection to PD'
		self.pd.close()
		print 'Closing socket thread...'
		kill_thread = True