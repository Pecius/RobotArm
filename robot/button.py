class Button:
	def __init__(self, pin, key):
		pin.init(pin.IN, pin.PULL_UP)
		
		self.pin = pin
		self.key = key
		self.state = True
	
	def onKeyDown(self, handler):
		self.onKeyDownH = handler
		
	def onKeyUp(self, handler):
		self.onKeyUpH = handler
	
	def isDown(self):
		return not self.state
	
	async def run(self):
		while(True):
			yield 20
			p = self.pin()
			
			if(p != self.state):
				self.state = p
				
				if(p):
					if(self.onKeyUpH):
						self.onKeyUpH(self.key)
						
				else:
					if(self.onKeyDownH):
						self.onKeyDownH(self.key)