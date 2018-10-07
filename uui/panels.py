from uui.core import *

class LongText(InteractivePanel):
	def __init__(self, parent, width, height, text = None):
		super().__init__(parent)
		self.setupManualUpdate()
		
		lines = []
				
		for i in range(height):
			mv = memoryview(bytearray(b" " * width))
			lines.append(mv)
			self.addElement(mv, 0, i)
		
		self.entryLen = width
		self.lines = lines
		self.pos = 0
		
		if(text):
			self.setText(text)
		
	def setText(self, text):
		self.text = memoryview(text)
		self.pos = 0
		self.updateText()
		
	def updateText(self):
		if(not self.text):
			return
		
		tLen = len(self.text)
		eLen = self.entryLen
		pos = self.pos * eLen
		
		for k, l in enumerate(self.lines):
			lpos = pos + k * eLen
			
			if(lpos + eLen <= tLen):
				l[:] = self.text[lpos : lpos + eLen]
			else:
				nl = tLen - lpos 

				if(nl > 0):
					l[:nl] = self.text[lpos: lpos + nl]
					
				for i in range(max(nl, 0), eLen):
					l[i] = ord(b" ")
		
		self.setUpdate()
	
	def scroll(self, inc):
		pos = self.pos + (1 if inc else -1)
		
		if(pos < 0 or pos * self.entryLen > len(self.text)):
			return
			
		self.pos = pos
		
		self.updateText()
	
	def onKeyDown(self, key):
		if(key in b"\x28\x26"):
			self.scroll(key == 0x28)
		
		
		
		
		
class Menu(InteractivePanel):
	class Entry:
		def __init__(self, line):
			self.line = line
			
		def __call__(self):
			try:
				return self.entries[self.parent.entryPos + self.line]
			except:
				return b""
			

	def __init__(self, parent, lines, cursor = b">"):
		super().__init__(parent)
		self.setupManualUpdate()
		
		self.entries = []
		
		self.cursorPos = 0
		self.entryPos = 0
		self.lines = lines
		
		self.cursor = self.addElement(cursor)
		
		class cEntry(self.Entry):
			parent = self
			entries = self.entries
		
		cursorlen = len(cursor)
		
		for l in range(lines):
			self.addElement(cEntry(l), cursorlen, l)

		
	def addEntry(self, str):
		self.entries.append(str)
		
	def select(self, pos):
		self.scroll(pos - self.entryPos)
	
	def enter(self):
		pos = self.entryPos + self.cursorPos
	
		if(pos < len(self.entries)):
			self.onEnter(self.entries[pos])
			
	
	def scroll(self, value):
		csum = self.cursorPos + value
		top = len(self.entries) - self.lines
		
		if(csum >= self.lines):
			self.entryPos += value - (self.lines - self.cursorPos - 1)
			self.cursorPos = self.lines - 1
			
		elif(csum < 0):
			self.entryPos += csum
			self.cursorPos = 0
		else:
			self.cursorPos = csum

		if(top < 0 and self.cursorPos >= len(self.entries)):
			self.cursorPos = len(self.entries) - 1

		if(self.entryPos > top):
			self.entryPos = top
			
		if(self.entryPos < 0):
			self.entryPos = 0
		
			
		self.cursor.setPos(0, self.cursorPos)
	
	def onKeyDown(self, key):
		if(key == 0x28):	# Encoder clockwise
			self.scroll(1)	
		elif(key == 0x26):	# Encoder counterclockwise
			self.scroll(-1)
		elif(key in b"\x0DA"):	# Enter (encoder) or A
			self.enter()
		elif(key in b"B"):
			self.onEnter(None)
		else:
			return
			
		self.setUpdate()
		
	def onEnter(self, entry):
		pass

class FileSelect(Menu):
	def __init__(self, parent, lines, onSelect, cursor = b">", dir = b"/", filter = None, last = None):
		super().__init__(parent, lines, cursor)
		
		self.dir = [dir]
		self.onSelect = onSelect
		self.filter = ure.compile(filter) if filter else None
		
		self.openDir(last = last)
		
	def __path_join(self, entry = None):
		if(entry):
			r = b"/".join(self.dir) + b"/" + entry
		else:
			r = b"/".join(self.dir)
				
		return r.replace(b"//", b"/")
	
	def openDir(self, dir = None, last = None):
		lastpos = 0
		entries = self.entries
		entries.clear()
	
		if(dir == b".."):
			last = self.dir.pop()
		elif(dir):
			for d in dir.split(b"/"):
				if(d):
					self.dir.append(d)
		
		path = self.__path_join()
		
		try:
			dirIter = uos.ilistdir(path)
		except OSError:
			print("Error, wrong path openDir", path)
			return
			
			
		if(len(self.dir) > 1):
			entries.append(b"..")
		
		for f, t, c in dirIter:
			if(last == f):
				lastpos = len(entries)
				
			if(f != b"." and f != b".."):
				if(t == 0x8000 and self.filter and not self.filter.match(f)):
					continue
			
				entries.append(f)

				
		self.select(lastpos)
		self.setUpdate()

	def onEnter(self, entry):
		if(entry is None):
			self.onSelect(None)
			return
	
		path = self.__path_join(entry)
		dir = True
	
		if(entry == b".."):
			self.openDir(entry)
			return
	
		try:
			uos.ilistdir(path)
		except OSError as err:
			if(err.args[0] == 20):
				dir = False
			else:
				print("Error, wrong path", path or "None")
				return
			
		if(dir):
			self.openDir(entry)
		else:
			self.onSelect(path)
			

class CheckBox(InteractivePanel):
	def __init__(self, parent, callback, state = False, mark = b"X", format = b"[%s]"):
		super().__init__(parent)
		self.setupManualUpdate()
		self.setCursor((format % b"\0").index(b"\0") + 1)
	
		self.callback = callback
		self.mark = mark
		self.format = format
		
		self.entry = self.addElement()
		self.setState(state)
		
	def setState(self, state = None):
		if(state is None):
			self.state = not self.state
		else:
			self.state = state
			
		self.entry.value = self.format % (state and self.mark or b" ")
		self.setUpdate()
		
	def onKeyDown(self, key):
		if(key in b"A"):
			self.callback(self.state)
		elif(key in b"B"):
			self.unfocus()
		elif(key == 0xD):
			self.setState()
			
class Button(InteractivePanel):
	def __init__(self, parent, text, callback):
		super().__init__(parent)
		self.setupManualUpdate()
		
		self.textEntry = self.addElement(text)
		self.callback = callback
		
		self.setUpdate()
		
	def setText(self, text):
		self.textEntry.value = text
		self.setUpdate()
		
	def onFocus(self):
		self.callback()
		self.unfocus()
		
class BaseEntry(InteractivePanel):
	def __init__(self, parent, len, name = None):
		super().__init__(parent)
		self.setupManualUpdate()
		
		self.text = memoryview(bytearray(b" " * (len + 1)))
		
		self.entry = self.addElement(self.text[:len])
		self.pos = 0
		self.toppos = 0
		self.len = len
		self.nameE = None
		
		if(name):
			self.setName(name)
	
	def setName(self, name):
		if(not self.nameE):
			self.nameE = self.addElement()
		
		self.nameE.value = name
		self.entry.setPos(len(name), 0)
		
		self.setCursorShift(len(name), 0)
		self.setCursor(self.pos)
		
		self.setUpdate()
	
	def setValue(self, value):
		l = len(value) if len(value) < self.len else self.len
		
		self.text[:l] = value[:l]
		
		for i in range(l, self.len):
			self.text[i] = ord(" ")
		
		self.pos = l
		self.toppos = l
		
		self.setCursor(self.pos)
		self.setUpdate()
	
	def accept(self, value):
		pass

	def insert(self, ch):
		pos = self.pos
		top = self.toppos
				
		if(pos >= self.len):
			return
			
		v = self.text
		
		if(pos != top):
			c = bytes(v[pos : top + 1])
			v[pos + 1 : top + 2] = c
		
		v[pos] = ch
	

		self.pos += 1
		self.toppos += 1
		
		self.setCursor(self.pos)
		self.setUpdate()
		
	def delete(self):
		v = self.text
		pos = self.pos
		top = self.toppos
		
		v[pos - 1 : top] = v[pos : top + 1]

		if(pos != top):
			v[top] = ord(b" ")
		
		self.pos -= 1
		self.toppos -= 1
		
		self.setCursor(self.pos)
		self.setUpdate()
		
	def replace(self, ch):
		self.text[self.pos] = ch
		
	def onKeyDown(self, key):
		if(key == 0x28):
			self.pos += 1
		elif(key == 0x26):
			self.pos -= 1
		elif(key in b"A"):
			self.accept(bytes(self.text[:self.toppos]))
		elif(key in b"B"):
			self.unfocus()
		elif(key in b"C" and self.pos != 0):
			self.delete()
		
			
		if(self.pos < 0):
			self.pos = 0
		if(self.pos > self.toppos):
			self.pos = self.toppos
		
		self.setCursor(self.pos)
		self.setUpdate()
			
class TextEntry(BaseEntry):
	def __init__(self, parent, onAccept, len, name = None):
		super().__init__(parent, len, name)
		self.onAccept = onAccept
		self.state = 0
	
	def accept(self, s):
		self.onAccept(s)
		self.unfocus()
	
	def onKeyDown(self, key):
		super().onKeyDown(key)
		if(key in b"C"):
			if(self.state == 1):
				self.state = 2
	
	def onMultiTap(self, key, final):
		if(self.state == 0):
			self.insert(ord(key))
			self.state = 1
		elif(self.state == 1):
			self.text[self.pos - 1] = ord(key)
		
		if(final):
			self.state = 0
			
class PasswordEntry(TextEntry):
	def __init__(self, parent, onAccept, len, name = None):
		super().__init__(parent, onAccept, len, name)
		
			
class NumberEntry(BaseEntry):
	def __init__(self, parent, onAccept, len = 6, name = None, float = False):
		super().__init__(parent, len, name)
		self.float = float
		self.onAccept = onAccept

	def accept(self, s):
		if(self.float):
			s = float(s)
		else:
			s = int(s)
			
		self.onAccept(s)
		self.unfocus()
		
	def setValue(self, value):
		if(self.float):
			value = b"%g" % value
		else:
			value = b"%d" % value
		
		super().setValue(value)
		
	def onKeyDown(self, key):
		super().onKeyDown(key)
		
		if(key >= ord(b"0") and key <= ord(b"9")):
			self.insert(key)

		elif(self.float and key in b"*"):
			self.insert(ord(b"."))