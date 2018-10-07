from uui.core import *
from uui.panels import *

class InteractiveScreen(Screen):
	def __init__(self, parent, w, h):
		super().__init__(parent)
		self.selectedPanel = None
		self.cursor = TextPanel(self, b">")
		#self.add(self.cursor)
		
		self.width = w
		self.height = h
		
	def add(self, panel, focus = False):
		super().add(panel, focus)
		
		if(focus and isinstance(panel, InteractivePanel)):
			x, y = panel.getPos()
			self.cursor.setPos(max(x - 1, 0), y)
			
		return panel

		
	def remove(self, panel):
		super().remove(panel)
		
		if(panel == self.selectedPanel):
			self.selectNext()
	
	def selectNext(self, next = True):
		if(self.selectedPanel):
			x, y = self.selectedPanel.getPos()
		else:
			x = 0
			y = 0
		
		minx = self.width if next else -1
		
		winner = None
		
		for p in self.panels:
			px, py = p.getPos()
			if(py == y and isinstance(p, InteractivePanel)):
				if((next and px > x and minx > px) or (not next and px < x and minx < px)):
					winner = p
					minx = px

		if(not winner):
			iter = range(y + 1, self.height) if next else range(max(y - 1, 0), -1, -1)
			for y in iter:
				for p in self.panels:
					px, py = p.getPos()
					if(py == y and isinstance(p, InteractivePanel)):
						if((next and minx > px) or (not next and minx < px)):
							winner = p
							minx = px
							
				if(winner):
					break

		if(winner):
			self.selectedPanel = winner			
			self.cursor.setPos(max(minx - 1, 0), y)
			
		self.needsUpdate = True
		
	def onKeyDown(self, key):
		if(key == 0x28):	# Encoder clockwise
			self.selectNext()	
		elif(key == 0x26):	# Encoder counterclockwise
			self.selectNext(False)
		elif(key == 0x0D):	# Enter (encoder)
			if(not self.selectedPanel):
				self.selectNext()
				
			if(self.selectedPanel):
				self.focus(self.selectedPanel)
	
	
	def draw(self, buff):
		for p in self.panels:
			p.draw(buff)
			
		self.cursor.draw(buff)
		buff.cursor = self.__focused and self.__focused.__cursor

class TextScreen(Screen):
	def __init__(self, parent, width, height, text = None):
		super().__init__(parent)
		
		self.longText = self.add(LongText(self, width, height, text), False)
		
	def onKeyDown(self, key):
		if(key in b"\x28\x26"):
			self.longText.scroll(key == 0x28)
		elif(key in b"\x0DAB"):
			self.destroy()
			
			
class DialogueScreen(InteractiveScreen):
	def __init__(self, parent, width, height = 3, desc = b"", options = None):
		super().__init__(parent, width, height)
		self.desc = self.add(TextPanel(self, desc))
	
	def onOption(self, opt):
		pass
		
		
class MenuScreen(Screen):
	def __init__(self, parent, lines, callback, entries = None):
		super().__init__(parent)
		self.callback = callback
		
		menu = self.add(Menu(self, lines), True)
		menu.onEnter = self.onSelect
		self.addEntry = menu.addEntry
		
		if(entries):
			for e in entries:
				self.addEntry(e)
		
	def onSelect(self, item):
		self.destroy()
		if(item != None):
			self.callback(item)
			
		
class FileScreen(Screen):
	def __init__(self, parent, lines, callback, dir = b"/", filter = None):
		super().__init__(parent)
		self.callback = callback
		
		fs = self.add(FileSelect(self, lines, self.onFile, dir = dir, filter = filter), True)
		self.openDir = fs.openDir
		
	def onFile(self, file):
		self.destroy()
		
		if(file != None):
			self.callback(file)
		

	