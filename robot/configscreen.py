import uui
import network
from wlanstate import wlanState
import network
import machine


class WifiDialog(uui.Screen):
	def __init__(self, parent, ssid, callback):
		super().__init__(parent)
		self.callback = callback
		self.ssid = ssid
		
		self.add(uui.TextPanel(self, b"SSID: %s" % ssid))
		
		self.add(uui.TextPanel(self, b"Pass:")).setPos(0, 1)
		
		self.add(uui.TextEntry(self, self.onEnter, 20), True).setPos(0, 2)

	def onEnter(self, pw):
		self.destroy()
		self.callback(self.ssid, pw)
		
	def unfocus(self):
		super().unfocus()
		self.destroy()
		
class WifiScreen(uui.InteractiveScreen):
	def __init__(self, parent):
		super().__init__(parent, 20, 4)
		self.wlan = network.WLAN(network.STA_IF)
		
		self.wifiEnable = self.add(uui.CheckBox(self, self.onWiFiChange, machine.nvs_getint("wifiEnabled"), format = b"Enabled [%s]"))
		self.wifiEnable.setPos(1, 0)
		
		self.wifiButton = self.add(uui.Button(self, b"WiFi: %s" % (wlanState.ssid or b"None"), self.onWiFiOpen), False)
		self.wifiButton.setPos(1, 1)
		
		self.ipstate = self.add(uui.TextPanel(self, b"IP: %s" % self.wlan.ifconfig()[0]))
		self.ipstate.setPos(1, 2)
		
		self.wifiStatus = self.add(uui.TextPanel(self))
		
	def onWiFiChange(self, value):
		machine.nvs_setint("wifiEnabled", value and 1 or 0)
		self.wlan.active(value)
		
	def onWiFiSelect(self, ap):
		self.setScreen(WifiDialog(self, ap, self.onWiFiConnect))
		
	def onWiFiConnect(self, ssid, pw):
		self.wlan.connect(ssid, pw)
		
	def onWiFiOpen(self):
		if(not machine.nvs_getint("wifiEnabled")):
			return
	
		menu = uui.MenuScreen(self, 4, self.onWiFiSelect)
		
		aps = self.wlan.scan()
		
		for ap in aps:
			menu.addEntry(ap[0])
			
		self.setScreen(menu)
		
	def onKeyDown(self, key):
		super().onKeyDown(key)
		if(key in b"B"):
			self.destroy()
	
class NetworkScreen(uui.InteractiveScreen):
	def __init__(self, parent):
		super().__init__(parent, 20, 4)
		
		self.telnetEnable = self.add(uui.CheckBox(self, self.onTelnetChange, machine.nvs_getint("telnetEnabled"), format = b"Telnet [%s]"))
		self.telnetEnable.setPos(1, 0)
		
		self.telnetEnable = self.add(uui.CheckBox(self, self.onFTPChange, machine.nvs_getint("ftpEnabled"), format = b"FTP [%s]"))
		self.telnetEnable.setPos(1, 1)
		
		log = self.add(uui.TextEntry(self, self.onLogin, 20, name = b"L:"), False)
		log.setPos(1, 2)
		log.setValue(machine.nvs_getstr("networkLogin").encode())
		
		pas = self.add(uui.TextEntry(self, self.onPassword, 20, name = b"P:"), False)
		pas.setPos(1, 3)
		
		
	def _update(self):		
		user = machine.nvs_getstr("networkLogin")
		password = machine.nvs_getstr("networkPassword")
		
		if(machine.nvs_getint("ftpEnabled")):
			network.ftp.start(user = user, password = password)
		else:
			network.ftp.stop()
		
		if(machine.nvs_getint("telnetEnabled")):
			network.telnet.start(user = user, password = password)
		else:
			network.telnet.stop()
		
	def onPassword(self, pwd):
		machine.nvs_setstr("networkPassword", pwd)

	def onLogin(self, login):
		machine.nvs_setstr("networkLogin", login)
		
	def onFTPChange(self, value):
		machine.nvs_setint("ftpEnabled", value and 1 or 0)
		
	def onTelnetChange(self, value):
		machine.nvs_setint("telnetEnabled", value and 1 or 0)
	
	def onKeyDown(self, key):
		super().onKeyDown(key)
		if(key in b"B"):
			self._update()
			self.destroy()