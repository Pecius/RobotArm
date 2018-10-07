from socket import socket, getaddrinfo
import machine

from robot.input import keyDown, keyUp
import _thread as thread

SE = 240
AYT = 246
IAC = 255
SB = 250
WILL = 251
WONT = 252
DO = 253
DONT = 254
TRANSMIT_BINARY = 0
ECHO = 1
SUPPRESS_GO_AHEAD = 3
LINEMODE = 34
MODE = 1
EDIT = 1


options = bytes([IAC, WILL, ECHO, IAC, WILL, SUPPRESS_GO_AHEAD, IAC, WONT, LINEMODE])
options_user = bytes([IAC, WONT, ECHO, IAC, WONT, SUPPRESS_GO_AHEAD, IAC, WILL, LINEMODE])
options_pass = bytes([IAC, WILL, ECHO, IAC, WONT, SUPPRESS_GO_AHEAD, IAC, WILL, LINEMODE])


class TelnetMirror:	
	def startServer(self):
		addr = getaddrinfo("0.0.0.0", 33)[0][4]
		self.server = socket()
		self.server.bind(addr)
		self.server.listen(1)
		
		#start_new_thread("UIMirror", self.run, (), None, True)
		
		self.client = None
		
	def setCursor(self, x, y):
		if(not self.client):
			return
	
		self.client.write(b"\x1b[%d;%d" % (x, y))

	def write(self, line, str):
		s = self.client
		
		if(not s):
			return
		
		
		s.write(b"\x1b[0;%d" % line)
		s.write(str)
	
	def run():
		server = self.server
		
		while(True):
			cl = server.accept()[0]
			self.client = cl
			
			try:
				cl.send(options_user)
				cl.send(b"Login: ")
				login = cl.recv(20).strip()
			
				cl.send(options_pass)
				cl.send(b"Password: ")
				password = cl.recv(20).strip()

				if(login != machine.nvs_getstr("networkLogin") or password != machine.nvs_getstr("networkPassword")):
					self.client = None
					cl.close()
					continue
				
			except:
				self.client = None
				cl.close()
				continue
			
			
			cl.send(options)
			
			try:
				while(True):
					c = cl.recv(1)
					keyDown(ord(c))
					keyUp(ord(c))
			except OSError as e:
				print(e)
			
			self.client = None
			cl.close()
			
