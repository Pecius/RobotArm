# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'

import _thread
import machine

def startWifi():
	import network
	import utime
	import machine
	machine.loglevel("wifi", machine.LOG_ERROR)
	
	wlan = network.WLAN(network.STA_IF)
	wlan.active(True)
	wlan.connect(machine.nvs_getstr("wifiSSID"), machine.nvs_getstr("wifiPass"))

	
	while(not wlan.isconnected()):
		utime.sleep_ms(50)

	user = machine.nvs_getstr("networkLogin")
	password = machine.nvs_getstr("networkPassword")
	
	network.ftp.start(user = user, password = password)
	network.telnet.start(user = user, password = password)
	
#	print("WiFi started")
	

_thread.start_new_thread("WiFiInit", startWifi, ())

import robot