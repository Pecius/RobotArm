from utime import ticks_ms, ticks_diff
from micropython import const

_IDLE		= const(0)
_DOWN		= const(1)
_UP			= const(2)
_HOLD		= const(3)
_SINGLEHOLD	= const(4)

_KEYMODE	= b"\xA0"

standardLayout = {
	ord("1"): b"1",		ord("2"): b"abc2",	ord("3"): b"def3",
	ord("4"): b"ghi4",	ord("5"): b"jkl5",	ord("6"): b"mno6",
	ord("7"): b"pqrs7",	ord("8"): b"tuv8",	ord("9"): b"wxyz9",
	ord("*"): b" ",		ord("0"): b"0",		ord("#"): _KEYMODE
}

class MultiTap:
	def __init__(self, layout = standardLayout, multitapTimeout = 1000, longpressTimeout = 1000):
		self.layout = layout
		
		self.multitapTimeout = multitapTimeout
		self.longpressTimeout = longpressTimeout
		
		self.key		= None
		self.time = 0
		self.state = _IDLE
		
		self.pos	= -1
		self.mode	= 0
	
		
	def onKey(self, handler):
		self.onKeyH = handler
		
	def keyDown(self, key):
		if(key in self.layout):
			self.process(key, True)
		
	def keyUp(self, key):
		if(key in self.layout):
			self.process(key, False)
		
	def callHandler(self, final = False):		
		ch = self.layout[self.key][self.pos]
		
		if(final and ch == _KEYMODE[0]):
			self.mode += 1
			
			if(self.mode > 3):
				self.mode = 0
				
			#if(self.mode == 3):
			return
				
		ch = chr(ch)
		
		if(self.mode == 1):
			ch = ch.upper()
			if(final):
				self.mode = 0
		elif(self.mode == 2):
			ch = ch.upper()
		
		self.onKeyH(ch, final)

	
	def process(self, key = None, down = False):
		s = self.state
		
		if(s == _HOLD):
			if(not down and key == self.key):
				self.time = ticks_ms() + self.multitapTimeout
				s = _UP
				#print("HOLD not key")
				
			elif(down and key != self.key):
				self.callHandler(True)
				s = _IDLE
				#print("HOLD key != self.key")
				
			elif(ticks_diff(self.time, ticks_ms()) <= 0):
				self.pos = len(self.layout[self.key]) - 1
				self.callHandler(True)
				s = _IDLE
				#print("HOLD ticks_diff(self.time, ticks_ms()) <= 0")
				
		elif(s == _SINGLEHOLD):
			if(not down or key != self.key):
				s = _IDLE
				
		elif(s == _UP):
			if(down and key == self.key):
				s = _DOWN
				#print("UP key == self.key")
			#elif((down and key != self.key) and key == )	edit key if special
			
			elif((down and key != self.key) or ticks_diff(self.time, ticks_ms()) <= 0):
				self.callHandler(True)
				s = _IDLE
				#print("(UP key and key != self.key) or ticks_diff(self.time, ticks_ms()) <= 0", (down and key != self.key))
				
				
		if(s == _IDLE):
			if(down and key):
				s	= _DOWN
				self.key	= key
				self.pos	= -1
				#print("IDLE")
				
		if(s == _DOWN):
			l = len(self.layout[self.key]) - 1
			
			if(l == 0):
				self.callHandler(True)
				s = _SINGLEHOLD
			elif(self.mode == 3):
				self.pos = l
				self.callHandler(True)
				s = _SINGLEHOLD
			else:
				self.pos = self.pos + 1 if self.pos < l else 0
				self.callHandler()
				self.time = ticks_ms() + self.longpressTimeout
				s = _HOLD
			#print("DOWN")
			
			
		self.state = s