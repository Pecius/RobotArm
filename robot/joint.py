from micropython import const
from robot import ucoroutine

from utime import sleep_ms
import _thread as thread

_DELAY = const(5)
_TDELAY = const(_DELAY - 2)
round = round

class JointGroup:
	def __init__(self, *args):
		self.joints = args
	
	def setBounds(self, min, max):
		for j in self.joints:
			j.setBounds(min, max)
			
	def getBounds(self):
		return self.joints[0].getBounds()
		
	def rotate(self, degree, instant = False, raw = False):
		if(raw):
			for k, v in enumerate(degree):
				self.joints[k].rotate(v, instant, raw)
		else:
			for j in self.joints:
				j.rotate(degree, instant, raw)
			
	def setSpeed(self, speed):
		for j in self.joints:
			j.setSpeed(speed)
			
	def calcRotation(self, deg):
		res = []
		for j in self.joints:
			res.append(j.calcRotation(deg))
			
		return res
		
	def getRotation(self, pos = None):
		return self.joints[0].getRotation(pos)

		

from utime import ticks_ms, ticks_diff
	
class ServoJoint:
	def __init__(self, servo, inverse = False, minDeg = 0, maxDeg = 180, center = 0, topSpeed = 60/170):
		self.servo = servo
		
		self.inverse = inverse
		
		self.curPos = servo.toRaw(0)
		self.newPos = self.curPos
		
		self.minDegree = minDeg
		self.maxDegree = maxDeg
		self.center = servo.makeOffset(center, inverse)
		
		self.topSpeed = self.servo.degmul * topSpeed
		self.speed = self.topSpeed

		
	def setBounds(self, min, max):
		self.minDegree = min
		self.maxDegree = max
		
	def getBounds(self):
		return self.minDegree, self.maxDegree

	def setSpeed(self, speed):		
		if(speed < 0 or speed > 100):
			raise ValueError("Invalid speed value, should be between 0 and 100")
			
		self.speed = (speed/100) * self.topSpeed
	
	def calcRotation(self, deg):
		if(self.minDegree > deg or deg > self.maxDegree):
			raise ValueError("Invalid degree %d (%d - %d)" % (deg, self.minDegree, self.maxDegree)) 
			return
	
		return self.servo.toRaw(deg, self.center, self.inverse)
		
	def getRotation(self, pos = None):
		return self.servo.toDegree(pos or self.curPos, self.center, self.inverse)
	
	def rotate(self, deg, instant = False, raw = False):
		if(not raw):
			self.newPos = self.calcRotation(deg)
		else:
			self.newPos = deg
		
		if(instant):
			self.servo.setRaw(self.newPos)
			self.curPos = self.newPos
		


class JointRunner:
	def __init__(self, appcore = False):
		self.joints = []
		self.running = False
		self.syncMode = False
		
		self.thread = thread.start_new_thread("JointRunner", self.__threadfunc, (), None, appcore)
		

	
	def add(self, joint):
		joints = self.joints
	
		if(isinstance(joint, JointGroup)):
			for j in joint.joints:
				joints.append(j)
				
		else:
			joints.append(joint)
	
	def run(self, sync = False):
		self.syncMode = sync
		self.running = True

		thread.notify(self.thread, 1)
		
		return self.wait()
		
	async def wait(self):
		while(self.running):
			yield _DELAY * 4
			
	def __threadfunc(self):
		while(True):
			self.running = False
			self.joints.clear()
			
			thread.wait()
			ntf = thread.getnotification()
			
			if(ntf == thread.STOP):	
				return
			
			sync = self.syncMode
			
			if(sync):
				top = -1
				synctime = None
				
				for j in self.joints:
					r = abs(j.curPos - j.newPos)
					
					if(r > top):
						top = r
						synctime = r / j.speed
		
			
			jdata = []
			for j in self.joints:
				posdiff = abs(j.curPos - j.newPos)
				if(posdiff == 0):
					continue
				
				if(sync):
					step = _DELAY * (posdiff / synctime)
				else:
					step = _DELAY * j.speed
				
				steps = int(posdiff / step)
				step *= 1 if j.curPos < j.newPos else -1
				
				jdata.append([j.curPos, steps, step, j.servo.setRaw, j.newPos])
				
				j.curPos = j.newPos
				
			jdata.sort(key = lambda x: x[1], reverse = True)
			jlen = len(jdata)
			
			pos = jlen
			while(jlen):
				while(pos):
					pos -= 1
					
					j = jdata[pos]
					j[1] -= 1		# steps - 1
					j[0] += j[2]	# curPos + step
					
					if(j[1] <= 0):	# steps == 0
						j[3](round(j[4]))	# j.setRaw(j.newPos)
						jlen -= 1
					else:
						j[3](round(j[0])) # j.setRaw(j.curPos)
					
				
				pos = jlen
				sleep_ms(_TDELAY)
				
		
