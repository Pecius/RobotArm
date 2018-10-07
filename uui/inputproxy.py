class InputServer:
	def __init__(self):
		self.client = None

	def bind(self, cl):
		self.client = cl
	
	
	def unbind(self):
	
		self.client = None
	
	def getLastClient(self):
		cn = self.client
		cl = None
		
		while cn:
			cl = cn
			cn = cl.client
		
		return cl
	
	def keyDown(self, key):
		cl = self.getLastClient()
		if(not cl or not cl.onKeyDownH):
			return
			
		cl.onKeyDownH(key)
		
	def keyUp(self, key):
		cl = self.getLastClient()
		if(not cl or not cl.onKeyUpH):
			return
			
		cl.onKeyUpH(key)
		
	def multitap(self, key, final):
		cl = self.getLastClient()
		if(not cl or not cl.onMultiTapH):
			return
		
		cl.onMultiTapH(key, final)
		

class InputProxy:
	def __init__(self):
		self.client = None
		
		self.onKeyDownH = None
		self.onKeyUpH = None
		self.onMultiTapH = None
		
	def bind(self, cl):
		self.client = cl
	
	def unbind(self):
		self.client = None
		
	def onKeyDown(self, handler):
		self.onKeyDownH = handler
		
	def onKeyUp(self, handler):
		self.onKeyUpH = handler
		
	def onMultiTap(self, handler):
		self.onMultiTapH = handler