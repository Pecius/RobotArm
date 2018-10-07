import uui
from robot.program import ParserError
import robot.configscreen as cs

class ProgramDisplay(uui.Panel):
	__statetab = [b"S", b"R", b"P", b"E"]

	def __init__(self, parent, pgm, lines, cursor = b">"):
		super().__init__(parent)
		self.cursor = self.addElement(cursor)
		
		self.pgmObj = pgm
		self.pos = 0
		self.sPosX = 0
		self.topLen = 0
		
		self.pgmLines = []
		self.lines = []
		
		self.pgmFile = None
		
		cursorlen = len(cursor)
		for l in range(lines):
			self.lines.append(self.addElement(b"", cursorlen, l))
			
		self.stateIndicator = self.addElement(b"S", 0, lines)
		self.lineIndicator = self.addElement(b"0/0", 2, lines)
		self.curState = 0
		
	def openProgram(self, path):
		if(not path):
			self.pgmFile = None
			return
	
		pgmLines = []
		
		top = 0
		
		f = open(path, "rb")
		for l in f:
			pgmLines.append(f.tell())
			
			l = len(l)
			if(l > top):
				top = l

		f.close()
		
		self.topLen = top
		self.pgmLines = pgmLines
		self.pgmFile = path
		
	def updateLines(self):
		if(not self.pgmFile):
			return
		
		lines = self.lines
		pos = self.pos
		pglines = self.pgmLines
	
		if(pos - 1 >= 0):
			seek = pglines[pos - 1]
		else:
			seek = 0
		
		#print(pos, len(lines), pos + len(lines) - 1)

		if(pos + len(lines) > len(pglines)):
			rlen = pglines[-1]
		else:
			rlen = pglines[pos + len(lines) - 1]
			
		
		f = open(self.pgmFile, "rb")
		f.seek(seek)
		str = f.read(rlen - seek)
		f.close()

		split = str.splitlines()		#TODO
		
		for k, v in enumerate(lines):
			try:
				v.value = memoryview(split[k])[self.sPosX:]
			except IndexError:
				v.value = b""
		
	def update(self):
		pgm = self.pgmObj
		cur = pgm.currentLine() - 1
		state = pgm.programState
		
		if(state != self.curState):
			self.stateIndicator.value = self.__statetab[state]
			self.curState = state
			
			if(state == 3):
				self.parent.displayError(pgm.lastError.__str__())
				
			self.__update = True
		
		if(pgm.programFile != self.pgmFile):
			self.openProgram(pgm.programFile)
			self.sPosX = 0
			self.pos = -1

		if(cur != self.pos):
			self.pos = cur
			self.updateLines()
			self.lineIndicator.value = b"%d/%d" % (cur, len(self.pgmLines))
			
			return True
			
		u = self.__update
		self.__update = False
		return u
		
	def scroll(self, inc):
		pos = self.sPosX + (1 if inc else -1)
		
		if(pos < 0 or pos > self.topLen):
			return
			
		self.sPosX = pos
			
		self.updateLines()
		self.__update = True
		
		
class PoseSaveScreen(uui.Screen):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.add(uui.TextPanel(b"Pose name:"))

		namePanel = self.add(uui.TextEntry(self, self.onName, 20), True)
		namePanel.setPos(0, 1)
		namePanel.setValue(b"")
		
	def onName(self, name):
		pass

		
class ManualControlScreen(uui.InteractiveScreen):
	def __init__(self, parent, robotArm):
		super().__init__(parent, 20, 4)
		
		self.robotArm = robotArm
		self.joints = robotArm.joints
		
		self.curJointNum = 0
		self.curJoint = self.joints[0]
		self.limits = self.curJoint.getBounds()
		
		self.step = 1
		self.lockEncoder = False
		
		values = []
		
		for j in self.joints:
			values.append(j.getRotation())
			#print(j.getRotation())
			
		self.values = values
		
		self.jointText = self.add(uui.TextPanel(self, b"J: %d (%g*-%g*)" % (self.curJointNum + 1, self.limits[0], self.limits[1])))
		
		valueEntry = self.add(uui.NumberEntry(self, self.setJointValue, 6, b"Angle: ", True))
		valueEntry.setPos(1, 2)
		valueEntry.setValue(values[0])
		
		stepEntry = self.add(uui.NumberEntry(self, self.setStepValue, 6, b"Step: ",  True))
		stepEntry.setPos(1, 1)
		stepEntry.setValue(self.step)
		
		
		self.valueEntry = valueEntry
		self.stepEntry = stepEntry
		
		self.selectNext()
		
		
	def setJointValue(self, value):
		value = max(min(value, self.limits[1]), self.limits[0])
	
		self.values[self.curJointNum] = value
		self.valueEntry.setValue(value)
		
		self.joints[self.curJointNum].rotate(value, True)
		
	def setStepValue(self, value):
		self.step = value
	
	def incrementJointValue(self, inc = True):
		v = self.values[self.curJointNum]
		v += self.step if inc else -self.step
		
		self.setJointValue(v)
	
	def changeJoint(self, num):	
		if(num - 1 >= len(self.joints)):
			return
			
		self.curJointNum = num - 1
		self.curJoint = self.joints[num - 1]
		self.limits = self.curJoint.getBounds()
		
		self.valueEntry.setValue(self.curJoint.getRotation())
		
		self.jointText.setValue(b"J: %d (%g*-%g*)" % (num, self.limits[0], self.limits[1]))
	
	def selectPose(self, poseName):
		pose = self.robotArm.poses[poseName]
		joints = self.joints
		values = self.values
		
		for j, p in pose:
			i = joints.index(j)
			if(isinstance(p, list)):
				p = p[0]

				
			value = j.getRotation(p)
			self.values[i] = value
			
			if(i == self.curJointNum):
				self.valueEntry.setValue(value)
				
			#self.joints[i].rotate(value, True)
		
		self.robotArm.setSyncMode(True)
		self.robotArm.setSpeed(50)
		self.robotArm.applyPose(poseName)
			
			
		#for k, v in enumerate(values):
			
	
	def onKeyDown(self, key):
		if(not self.lockEncoder):
			super().onKeyDown(key)
		else:
			if(key in b"\x28\x26"):
				self.incrementJointValue(key == 0x28)
				return

		if(key >= ord(b"1") and  key <= ord(b"9")):
			self.changeJoint(key - ord(b"0"))
	
		elif(key in b"*"):
			self.lockEncoder = not self.lockEncoder
			
		elif(key in b"#"):
			ms = uui.MenuScreen(self, 4, self.selectPose, self.robotArm.poses.keys())
			self.setScreen(ms)
		elif(key in b"A"):
			pass #name and save to file
		elif(key in b"B"):
			self.destroy()
		elif(key in b"D"):
			self.robotArm.toggleGripper()
		
		
class ProgramScreen(uui.Screen):
	def __init__(self, parent, robotArm, lines):
		super().__init__(parent)
		self.robotArm = robotArm
		
		self.pd = self.add(ProgramDisplay(self, robotArm.program, lines), True)
	
	def onFileSelected(self, file):
		try:
			self.robotArm.loadProgram(file)
		except ParserError as e:
			print(e)
			self.displayError(e.__str__())
		#except Exception as e:
		#	print(e)
		#	self.displayError(bytes(e))
		
	def displayError(self, err):
		self.setScreen(uui.TextScreen(self, 20, 4, err))
	
	def onKeyDown(self, key):
		if(key in b"\x28\x26"):
			self.pd.scroll(key == 0x28)
	
		elif(key in b"1"):
			fs = uui.FileScreen(self, 4, self.onFileSelected, filter = b"\S+\.txt")
			self.setScreen(fs)
			
			file = self.robotArm.program.programFile
			if(file):
				file = file.rpartition(b"/")
				fs.openDir(file[0], file[2])
			
			
		elif(key in b"A"):
			self.robotArm.program.start()
		elif(key in b"B"):
			self.robotArm.program.pause()
		elif(key in b"C"):
			self.robotArm.program.stop()
		elif(key in b"*"):
			self.robotArm.program.stop()
			self.setScreen(ManualControlScreen(self, self.robotArm))
		elif(key in b"2"):
			self.setScreen(cs.WifiScreen(self))
			
		elif(key in b"3"):
			self.setScreen(cs.NetworkScreen(self))
		
		
		