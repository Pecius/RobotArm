from micropython import const

_DEF_DEGREE		= const(180)
_DEF_MAX_PULSE	= const(1500)
_DEF_MIN_PULSE	= const(500)


maxwidth  = 20000

def setFrequency(freq):
	global maxwidth
	maxwidth = int(1000000 / freq)
	
	
	
class CalibrationData:
	def __init__(self, pMin, pMax, mMin, mMax, deg, fDeg = 180, newMin = None):
		mul = (mMax - mMin) / deg
		if(newMin):
			rMin = newMin
		else:
			rMin = mMin + mul * ((deg - fDeg) / 2)
			
		rMax = rMin + mul * fDeg
		
		if(rMin < pMin):
			print("rMin < pMin")
		elif(rMax > pMax):
			print("rMax > pMax")
			
		self.data = (rMin, rMax, mul, fDeg)

class Servo:
	def __init__(self, pwm, caldata = (_DEF_MIN_PULSE, _DEF_MAX_PULSE, _DEF_DEGREE)):
		#self.pwm = pwm
	
		self.calibrate(caldata)
		
		self.setRaw = pwm.duty
		
	def calibrate(self, caldata):
		global maxwidth
		
		if(not isinstance(caldata, CalibrationData)):
			mul = (self.pwm.maxValue / maxwidth)
			caldata = CalibrationData(caldata[0] * mul, caldata[1] * mul, caldata[0] * mul, caldata[1] * mul, caldata[2], caldata[2])
	
		caldata = caldata.data
	
		self.minpulse	= caldata[0] #int(min * mul)
		self.maxpulse	= caldata[1] #int(max * mul)
		self.degmul		= caldata[2] #(max - min)/deg
		
		self.maxdeg		= caldata[3] #int(deg)
	
	def makeOffset(self, deg, inversed = False):
		if(inversed):
			return int(self.maxpulse - (deg * self.degmul + self.minpulse) + 0.5)
		else:
			return int(deg * self.degmul + 0.5)
	
	def toRaw(self, degree, offset = 0, inverse = False):
		if(not inverse):
			return int(0.5 + self.minpulse + self.degmul * degree) + offset
		else:
			return int(0.5 + self.maxpulse - self.degmul * degree) - offset
		
	def toDegree(self, rawValue, offset = 0, inverse = False):
		if(not inverse):
			return round(((rawValue - self.minpulse - offset) / self.degmul), 1)
		else:
			return round(((self.maxpulse - rawValue - offset) / self.degmul), 1)
	
	#def setRaw(self, value):	
	#	if(self.minpulse > value or value > self.maxpulse):
	#		raise ValueError("Raw value should be between %s and %s" % (self.minpulse, self.maxpulse))
	#		
	#	self.pwm.duty(value)
	
	def set(self, degree):
		if(degree < 0 or degree > self.maxdeg):
			raise ValueError("Degree should be between 0 and %s" % self.maxdeg)
			
		self.setRaw(int(0.5 + self.minpulse + self.degmul * degree))
