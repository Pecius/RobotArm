import utimeq
from utime import sleep_ms, ticks_ms, ticks_diff

StopIteration = StopIteration
next = next

class uCoroutine:
	def __init__(self, qlen = 16):
		self.queue = utimeq.utimeq(qlen)
		
	def add(self, gen):
		self.queue.push(ticks_ms(), gen, None)
	
	def run(self):
		q = self.queue
		task = [0,0,0]
		while(q):
			delay = ticks_diff(q.peektime(), ticks_ms())
			#print("delay", delay, q.peektime(), ticks_ms())
			sleep_ms(delay if delay > 0 else 0)

			q.pop(task)
			try:
				res = next(task[1]) or 0
				
				q.push(res + ticks_ms(), task[1], None)
			except StopIteration:
				pass
	
	async def runGen(self):
		q = self.queue
		task = [0,0,0]
		while(q):
			delay = ticks_diff(q.peektime(), ticks_ms())

			yield delay if delay > 0 else 0

			q.pop(task)
			try:
				res = next(task[1]) or 0
				
				q.push(res + ticks_ms(), task[1], None)
			except StopIteration:
				pass