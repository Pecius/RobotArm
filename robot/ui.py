from utime import sleep_ms
from _thread import getmsg

from machine import Encoder

from robot import multitap
from robot import ucoroutine
from robot import hd44780

import uui
from uui import inputproxy

from robot import hardware as hw
#from robot.telnet import TelnetMirror


map = {	0x48: ord("1"), 0x44: ord("2"), 0x42: ord("3"), 0x41: ord("A"),
		0x28: ord("4"), 0x24: ord("5"), 0x22: ord("6"), 0x21: ord("B"),
		0x18: ord("7"), 0x14: ord("8"), 0x12: ord("9"), 0x11: ord("C"),
		0x88: ord("*"), 0x84: ord("0"), 0x82: ord("#"), 0x81: ord("D")} 


async def processInput(mt, ip):
	while(True):
		yield 10
		msg = getmsg()
		if(msg[0]):
			mkey = msg[2]
			key = map[mkey & (0x100-1)] if mkey & 0x200 else mkey & (0x100-1)
			
			if(mkey & 0x100):
				#print("down", key)
				ip.keyDown(key)
				mt.keyDown(key)
			else:
				#print("up", key)
				ip.keyUp(key)
				mt.keyUp(key)
		else:
			mt.process()

			
async def updateDisplay(hd, server, buff, mirror):
	lines = [0, 40, 20, 84]

	while(True):	
		buff.clear()
		
		while(True):
			yield 50
			
			if(server.update()):
				break
		
		server.draw(buff)
		
		hd.turnOnCursor(False)
		
		for k, v in enumerate(buff):		
			while(True):
				try:
					hd.writeBulk(v, lines[k])
					break
				except OSError as e:	
					print(e)
					yield 50
					
			#mirror.write(k, buff)
		
		c = buff.cursor
		
		if(c):
			if(c[1] == 1):	# a workaround due to weirdness of LCD2004A
				hd.setAddress(lines[1])
				
				for i in range(c[0]):
					hd.shiftCursor()
			else:
				hd.setAddress(c[0] + lines[c[1]])
				
			hd.turnOnCursor()
			
			#mirror.setCursor(c[0], c[1])
			
			
hd = None
	

from robot import st
from robot.pdisp import ProgramScreen
	
def main():
	global hd
	encoder = Encoder(hw.encoderAPin, hw.encoderBPin)
	mt = multitap.MultiTap()
	inputServer = inputproxy.InputServer()
	
	hd = hd44780.HD44780(hd44780.FC113(hw.i2c, hw.displayAddress))
	sbuff = uui.ScreenBuffer(bytearray(b" "*20*4), 20, 4)
	server = uui.ScreenServer(inputServer)
	
	while(not st.ra):
		sleep_ms(20)
	
	screen = ProgramScreen(server, st.ra, 3)
		
	server.setScreen(screen)
	
	hd.init()
	sleep_ms(200)
	hd.clearDisplay()
	sleep_ms(100)
	hd.turnOnDisplay()
	sleep_ms(100)
	
	hd.initBulk(20)
	
	def onEnc(state):
		k = 0x28 if state == 0x10 else 0x26
		inputServer.keyDown(k)
		#inputServer.keyUp(k)
	
	encoder.callback(onEnc)
	mt.onKey(inputServer.multitap)
	
	tm = None #TelnetMirror()
	#tm.startServer()
	
	
	ms = ucoroutine.uCoroutine(2)
	ms.add(processInput(mt, inputServer))
	ms.add(updateDisplay(hd, server, sbuff, tm))
	
	ms.run()