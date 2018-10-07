from utime import sleep_ms

class Keypad4x4:
	__dummy = lambda x: None
	
	def __init__(self, iface):
		self.iface = iface
		self.keys = []
		self.last = [0] * 4
		
		self.onKeyDownH = self.__dummy
		self.onKeyUpH = self.__dummy
	
	def getKeys(self):
		return self.keys
		
	def onKeyDown(self, handler):
		self.onKeyDownH = handler
		
	def onKeyUp(self, handler):
		self.onKeyUpH = handler
	
	async def run(self):
		keys = self.keys
		last = self.last
	
		while(True):			
			for i in range(4):
				try:
					yield 5
					self.iface.write(i)
					yield 5
					res = self.iface.read()
				except OSError as err:
					print(err)
					continue
				
				if(last[i] != res):
					last[i] = res
					rc = 1 << (i + 4)
					
					for k in range(len(keys) - 1, -1, -1):
						v = keys[k]

						if(rc & v and res & v == 0):
							self.onKeyUpH(keys.pop(k))
					
					if(res != 0):
						for j in range(4):
							j = (1 << j)
							if(res & j != 0 and not (rc | j) in keys):
								keys.append(rc | j)
								self.onKeyDownH(rc | j)

class I2CIF:
	def __init__(self, i2c, address):
		self.i2c = i2c
		self.addr = address
		
		try:
			self.i2c.readfrom(self.addr, 1)
			
		except OSError:
			print("WEIRD I2C ERROR")
		
	def write(self, v):
		byte = bytearray(1)
		byte[0] = (1 << (v + 4)) ^ 0xFF
		
		self.i2c.writeto(self.addr, byte)
	
	def read(self):
		return (self.i2c.readfrom(self.addr, 1)[0] ^ 0xFF) & 0x0F
