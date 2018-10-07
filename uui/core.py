import uos
import ure
from uui import inputproxy

callable = callable
memoryview = memoryview
len = len
super = super
getattr = getattr

ord = ord
chr = chr

def installInputProxy(self):
	ip = inputproxy.InputProxy()
	
	if(getattr(self, "onKeyDown", False)):
		ip.onKeyDown(self.onKeyDown)
		
	if(getattr(self, "onKeyUp", False)):
		ip.onKeyUp(self.onKeyUp)
		
	if(getattr(self, "onMultiTap", False)):
		ip.onMultiTap(self.onMultiTap)

	self.inputproxy = ip

class BindAttribute:
	def __init__(self, obj, key):
		self.obj = obj
		self.key = key
		
	def __call__(self):
		return getattr(self.obj, self.key)
		

	
class BindItem:
	def __init__(self, obj, key):
		self.obj = obj
		self.key = key
		
	def __call__(self):
		return self.obj[self.key]
		

	
def BindFunction(fun):
	return fun
	
class Format:
	def __init__(self, fmt, obj):
		self.fmt = fmt
		self.obj = obj
		
	def __call__(self):
		return self.fmt % self.obj()
		

	

class Element:
	value = b""

	def __init__(self, value = None, x = 0, y = 0):
		pos = bytearray(2)
		pos[0] = x
		pos[1] = y
		
		if(callable(value)):
			self.getValue = value
		elif(value):
			self.value = value
		
		self.__pos = pos
		self.__show = True
		
	def getValue(self):
		return b""
	
	def setPos(self, x, y):
		self.__pos[0] = x
		self.__pos[1] = y
	
	def getPos(self):
		return self.__pos[0], self.__pos[1]
	
	def show(self, on = True):
		self.__show = on
		

class Panel:
	__update = True

	def __init__(self, parent):
		self.__elements = []
		self.parent = parent
		self.__pos = bytearray(2)
		self.__show = True
		
	def addElement(self, value = None, x = 0, y = 0):
		e = Element(value, x, y)
		self.__elements.append(e)
		
		return e
	
	def setupManualUpdate(self, manual = True):
		if(manual):
			self.update = self.__manualUpdate
		else:
			self.update = self.__alwaysUpdate
			
		
	def setUpdate(self):
		self.__update = True
	
	def show(self, on = True):
		self.__show = on
	
	def setPos(self, x, y):
		self.__pos[0] = x
		self.__pos[1] = y
		
	def getPos(self):
		return self.__pos[0], self.__pos[1]
	
	def destroy(self):
		self.parent.remove(self)
		
	def draw(self, buff):
		if(not self.__show):
			return
			
		blen = buff.width
		sx = self.__pos[0]
		sy = self.__pos[1]
		
		#buff = buff.b
		
		for e in self.__elements:
			if(e.__show):
				x = e.__pos[0] + sx
				y = e.__pos[1] + sy
				v = memoryview(e.value or e.getValue())
				l = len(v) if len(v) < (blen-x) else (blen-x)
				
				buff[y][x : x + l] = v[:l]
	
	def __alwaysUpdate(self):
		return True
		
	def __manualUpdate(self):
		u = self.__update
		self.__update = False
		return u
		
	update = __alwaysUpdate

class TextPanel(Element):
	__update = True

	def __init__(self, parent, value = None, x = 0, y = 0):
		super().__init__(value, x, y)


	def setValue(self, value):
		if(callable(value)):
			self.getValue = value
			self.value = None
		else:
			self.value = value
			
		self.__update = True

	def update(self):
		u = self.__update
		self.__update = False
		return u
		
	def draw(self, buff):
		if(self.__show):
			blen = buff.width
			#buff = buff.b
			
			x = self.__pos[0]
			y = self.__pos[1]
			v = memoryview(self.value or self.getValue())
			l = len(v) if len(v) < (blen-x) else (blen-x)
			
			buff[y][x : x + l] = v[:l]

	
class InteractivePanel(Panel):
	def __init__(self, parent):
		super().__init__(parent)
		installInputProxy(self)
		
		self.__cursor = None
		self.__cursorShift = bytearray(2)
		
	def setCursor(self, x = 0, y = 0):
		if(x is None):
			self.__cursor = None
		else:
			self.__cursor = bytearray([self.__pos[0] + self.__cursorShift[0] + x, self.__pos[1] + self.__cursorShift[1] + y])
			
	def setCursorShift(self, x = 0, y = 0):
		if(self.__cursor):
			self.__cursor[0] += x - self.__cursorShift[0]
			self.__cursor[1] += y - self.__cursorShift[1]
	
		self.__cursorShift[0] = x
		self.__cursorShift[1] = y
		
	def onFocus(self):
		pass
	
	def onUnfocus(self):
		pass
	
	def unfocus(self):
		self.parent.unfocus()
		
	def setPos(self, x, y):
		if(self.__cursor):
			self.__cursor[0] += x - self.__pos[0]
			self.__cursor[1] += y - self.__pos[1]
	
		self.__pos[0] = x
		self.__pos[1] = y
		
class Screen:
	def __init__(self, parent):
		self.parent = parent
		self.panels = []
		self.needsUpdate = False
		self.__focused = None
		
		installInputProxy(self)
		self.setScreen = parent.setScreen
		
	def draw(self, buff):
		for p in self.panels:
			p.draw(buff)
			
		buff.cursor = self.__focused and self.__focused.__cursor
			
	def update(self):
		if(self.needsUpdate):
			self.needsUpdate = False
			res = True
		else:
			res = False
		
		for p in self.panels:
			if(p.update()):
				res = True
				
		return res
		
	def add(self, panel, focus = False):
		self.panels.append(panel)
		
		if(focus and isinstance(panel, InteractivePanel)):
			self.focus(panel)
			
		self.needsUpdate = True
		
		return panel
		
	def remove(self, panel):	
		self.panels.remove(panel)
		
		if(panel == self.__focused):
			self.unfocus()
		
		self.needsUpdate = True
		
	def focus(self, panel):
		if(not panel in self.panels):
			raise ValueError("Panel not in panels")
	
		if(isinstance(panel, InteractivePanel)):
			self.inputproxy.bind(panel.inputproxy)
			self.__focused = panel
			panel.onFocus()
		else:
			self.inputproxy.unbind()
			self.__focused = None
	
		self.needsUpdate = True
			
	def unfocus(self):
		self.inputproxy.unbind()
		self.__focused = None
		
		self.needsUpdate = True
	
	def destroy(self):
		self.parent.setScreen(self.parent)