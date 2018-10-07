from micropython import const
import uctypes
from utime import sleep_ms
#from bytefifo import ByteFIFO


MODE_4BIT			= const(0)
MODE_8BIT			= const(1)

_FC113_RS			= const(1 << 0)
_FC113_RW			= const(1 << 1)
_FC113_E			= const(1 << 2)
_FC113_LED			= const(1 << 3)
_FC113_DATA_SHIFT	= const(4)

class FC113:
	mode = MODE_4BIT
	
	def __init__(self, i2c, address):
		self.i2c = i2c
		self.address = address
		
		self.led = _FC113_LED
		
	def initInterface(self):
		self.i2c.writeto(self.address, self.led)

	#def readNibble(self, data = False):
	#	byte = bytearray(1)
	#	byte[0] = _FC113_E | _FC113_RW | self.led | (_FC113_RS if data else 0) | ((1 << _FC113_DATA_SHIFT) - 1)
	#	self.i2c.writeto(self.address, byte)
	#	
	#	sleep_ms(1)
	#	res = self.i2c.readfrom(self.address, 1)[0] >> 4
	#	
	#	byte[0] &= _FC113_E ^ 0xFF
	#	self.i2c.writeto(self.address, byte)
	#	return res
	
	#def read(self, data = False):
	#	res = self.readNibble(data) << 4
	#	return res | self.readNibble(data)
		
	def writeNibble(self, nib, data = False):
		#byte = bytearray(1)
		byte = bytearray(2)
		byte[0] = _FC113_E | self.led | (_FC113_RS if data else 0) | nib << _FC113_DATA_SHIFT
		
		byte[1] = byte[0] & (_FC113_E ^ 0xFF)
		self.i2c.writeto(self.address, byte)
		
	def write(self, byte, data = False):
		self.writeNibble(byte >> 4, data)
		self.writeNibble(byte & 0xF, data)
	
	def initBulk(self, buffsize):
		self.bulkBuffer = memoryview(bytearray(4 + buffsize * 4))
	
	def writeBulk(self, inst, data):
		b = self.bulkBuffer
		bf = self.led
		bfe = bf | _FC113_E
		
		nsh = (inst >> 4) << _FC113_DATA_SHIFT
		b[0] = bfe | nsh
		b[1] = bf | nsh
		
		nsh = (inst & 0xF) << _FC113_DATA_SHIFT
		b[2] = bfe | nsh
		b[3] = bf | nsh
		
		bf = bf | _FC113_RS
		bfe = bf | _FC113_E
		
		bcnt = 4
		
		for c in data:
			nsh = (c >> 4) << _FC113_DATA_SHIFT
			b[bcnt]		= bfe | nsh
			b[bcnt + 1]	= bf | nsh
			
			nsh = (c & 0xF) << _FC113_DATA_SHIFT
			b[bcnt + 2]	= bfe | nsh
			b[bcnt + 3]	= bf | nsh
			
			bcnt += 4
	
		self.i2c.writeto(self.address, b[:bcnt])
		
	def backlight(self, on = True):
		self.led = _FC113_LED if on else 0

"""
class FC113Async(FC113):
	mode = MODE_4BIT
	
	def __init__(self, i2c, address, qlen = 160):
		super().__init__(i2c, address)
		self.queue = ByteFIFO(qlen)
		
	def write(self, byte, data = False):
		b = self.led | (_FC113_RS if data else 0)
		n1 = b | (byte >> 4) << _FC113_DATA_SHIFT
		n2 = b | (byte & 0xF) << _FC113_DATA_SHIFT
		
		self.queue.write(n1 | _FC113_E)
		self.queue.write(n1)
		
		self.queue.write(n2 | _FC113_E)
		self.queue.write(n2)
		
	async def run(self):
		q = self.queue
		a = self.address
		
		while(True):
			yield 5
			for i in q.read():
				self.i2c.writeto(self.address, i)
			
"""

_INSTR_CLEAR			= const(1 << 0)
_INSTR_RETURN			= const(1 << 1)

_INSTR_ENTRY_MODE		= const(1 << 2)
_INSTR_ENTRY_MODE_S		= const(1 << 0)
_INSTR_ENTRY_MODE_I		= const(1 << 1)

_INSTR_DISPLAY_CTRL		= const(1 << 3)
_INSTR_DISPLAY_DCTRL_B	= const(1 << 0)
_INSTR_DISPLAY_DCTRL_C	= const(1 << 1)
_INSTR_DISPLAY_DCTRL_D	= const(1 << 2)

_INSTR_CDSHIFT			= const(1 << 4)
_INSTR_CDSHIFT_R		= const(1 << 2)
_INSTR_CDSHIFT_S		= const(1 << 3)

_INSTR_FUNCTION_SET		= const(1 << 5)
_INSTR_FUNCTION_SET_F	= const(1 << 2)
_INSTR_FUNCTION_SET_N	= const(1 << 3)
_INSTR_FUNCTION_SET_DL	= const(1 << 4)

_INSTR_SET_CGRAM		= const(1 << 6)
_INSTR_SET_CGRAM_MASK	= const(_INSTR_SET_CGRAM - 1)

_INSTR_SET_DDRAM		= const(1 << 7)
_INSTR_SET_DDRAM_MASK	= const(_INSTR_SET_DDRAM - 1)

class HD44780:
	def __init__(self, iface):
		self.iface = iface
		self.displayControl = _INSTR_DISPLAY_CTRL
		
	def init(self, twolines = True, characters5x8 = True):
		i = self.iface
	
		if(self.iface.mode == MODE_4BIT):
			i.writeNibble(0x03)
			sleep_ms(5)
			i.writeNibble(0x03)
			sleep_ms(1)
			i.writeNibble(0x02)
		else:
			i.write(0x03)
			sleep_ms(5)
			i.write(0x03)
			sleep_ms(1)
			i.write(0x03)
		
		i.write(_INSTR_FUNCTION_SET | (_INSTR_FUNCTION_SET_DL if self.iface.mode == MODE_8BIT else 0)
		| (_INSTR_FUNCTION_SET_F if characters5x8 else 0) | (_INSTR_FUNCTION_SET_N if twolines else 0))
		
	def shiftCursor(self, right = True):
		self.iface.write(_INSTR_CDSHIFT | (_INSTR_CDSHIFT_R if right else 0))
	
	def shiftScreen(self, right = True):
		self.iface.write(_INSTR_CDSHIFT | _INSTR_CDSHIFT_S | (_INSTR_CDSHIFT_R if right else 0))
		
	def setEntryMode(self, increment = True, displayShift = True):
		self.iface.write(_INSTR_ENTRY_MODE | (_INSTR_ENTRY_MODE_I if increment else 0) | (_INSTR_ENTRY_MODE_S if displayShift else 0))

	def turnOnDisplay(self, on = True):
		if(on):
			self.displayControl |= _INSTR_DISPLAY_DCTRL_D
		else:
			self.displayControl &= _INSTR_DISPLAY_DCTRL_D ^ 0xFF
		
		self.iface.write(self.displayControl)
		
	def turnOnCursor(self, on = True, blink = False):
		self.displayControl &= (_INSTR_DISPLAY_DCTRL_C | _INSTR_DISPLAY_DCTRL_B) ^ 0xFF
		self.displayControl |= (_INSTR_DISPLAY_DCTRL_C if on else 0) | (_INSTR_DISPLAY_DCTRL_B if blink else 0)
		
		self.iface.write(self.displayControl)
	
	def clearDisplay(self):
		self.iface.write(_INSTR_CLEAR)
		
	def returnHome(self):
		self.iface.write(_INSTR_RETURN)
		
	def setAddress(self, addr, cgram = False):
		if(not cgram):
			self.iface.write(_INSTR_SET_DDRAM | (addr & _INSTR_SET_DDRAM_MASK))
		else:
			self.iface.write(_INSTR_SET_CGRAM | (addr & _INSTR_SET_CGRAM_MASK))
		
	def write(self, str):
		for c in str:
			self.iface.write(c, True)
	
	def initBulk(self, len):
		self.iface.initBulk(len)
	
	def writeBulk(self, data, addr = 0):
		self.iface.writeBulk(_INSTR_SET_DDRAM | (addr & _INSTR_SET_DDRAM_MASK), data)
		