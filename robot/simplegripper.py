class SimpleGripper:
	def __init__(self, pwm, openedVal, closedVal):
		self.closed = True
		self.setRaw = pwm.duty
		self.openedVal = openedVal
		self.closedVal = closedVal
		
		self.setRaw(closedVal)
		
	def open(self):
		self.closed = False
		self.setRaw(self.openedVal)
		
	def close(self):
		self.closed = True
		self.setRaw(self.closedVal)

	def toggle(self):
		if(self.closed):
			self.open()
		else:
			self.close()