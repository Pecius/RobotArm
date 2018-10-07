from uui.screens import *
 
class ScreenServer:
	def __init__(self, inputServer):
		self.screen = None
		self.inputServer = inputServer
	
	def setScreen(self, screen):
		self.screen = screen
		self.inputServer.bind(screen.inputproxy)
		
		self.draw = screen.draw
		self.update = screen.update
		
		screen.needsUpdate = True

	def update(self):
		pass
	
	def draw(self, buffer):
		pass


class ScreenBuffer(tuple):
	def __init__(self, buff, width, height):
		m = memoryview(buff)
		super().__init__(m[i * width :(i + 1) * width] for i in range(height))
		
		self.width = width
		self.height = height
		self.cursor = None
		self.clrBuff = b" " * 20
	
	def clear(self):
		for l in self:
			l[:] = self.clrBuff
	
	def __bytes__(self):
		tmp = []
		for l in self.b:
			tmp.append(str(bytes(l))[2:-1])
			tmp.append('\n')
			
			
		return "".join(tmp)
			
	__repr__ = __bytes__