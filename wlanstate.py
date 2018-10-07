from network import WLAN, STA_IF
import machine

class WlanState:
	def __init__(self):
		self.wlan = WLAN(STA_IF)
	
		self.wlan.eventCB(self.callback)
		self.ssid = None
		self.channel = None
		self.loginssid = None
		self.loginpass = None
	
	def connect(self, ssid, password):
		self.loginssid = ssid
		self.loginpass = password
		
		self.wlan.connect(ssid, password)
	
	def callback(self, info):
		id = info[0]
		desc = info[1]
		info = info[2]
		
		if(id == 4):
			self.ssid = info["ssid"]
			self.channel = info["channel"]
			
			if(self.ssid == self.loginssid):
				machine.nvs_setstr("wifiSSID", self.loginssid)
				machine.nvs_setstr("wifiPass", self.loginpass)
				
				self.loginssid = None
				self.loginpass = None
			
			
		elif(id == 5):
			self.ssid = None
			self.channel = None
			
wlanState = WlanState()