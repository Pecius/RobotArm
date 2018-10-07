from _thread import sendmsg
from micropython import const

from robot import ucoroutine

from robot.keypad import Keypad4x4, I2CIF
from robot.button import Button

from robot import hardware as hw

from robot import threads


keypad = None
enterButton = None

_KEYDOWN = const(0x100)
_RAWKEY = const(0x200)


def rawKeyDown(key):
	sendmsg(threads.UI, _KEYDOWN | _RAWKEY | key)
	
def rawKeyUp(key):
	sendmsg(threads.UI, _RAWKEY | key)
	
def keyDown(key):
	sendmsg(threads.UI, _KEYDOWN | key)
	
def keyUp(key):
	sendmsg(threads.UI, key)


def main():
	global keypad
	global enterButton

	keypad = Keypad4x4(I2CIF(hw.i2c, hw.keypadAddress))
	enterButton = Button(hw.encoderButton, 0x0D)
	
	keypad.onKeyDown(rawKeyDown)
	keypad.onKeyUp(rawKeyUp)
	
	enterButton.onKeyDown(keyDown)
	enterButton.onKeyUp(keyUp)
	
	ms = ucoroutine.uCoroutine(2)
	ms.add(keypad.run())
	ms.add(enterButton.run())
	
	ms.run()

#hread = start_new_thread("Input", main, (), {}, False)