

WifiManager = {};


function WifiManager.init(appName, useTimer, average)
	local self = {}
    
    self.appName = appName
    self.uniqueName = appName...node.chipid()
    
    wifi.setmode(wifi.STATIONAP)
    
    self.isConfigured = false
    
    --wifi.sta.eventMonReg()--
    --wifi.sta.eventMonStart()--
    
	self.time_start = 0
	self.time_end = 0
	self.trig = pin_trig or 4
	self.echo = pin_echo or 3
	gpio.mode(self.trig, gpio.OUTPUT)
	gpio.mode(self.echo, gpio.INT)
	self.average = average or 3

	function self.echo_cb(level)
		if level == 1 then
			self.time_start = tmr.now()
			gpio.trig(self.echo, "down")
		else
			self.time_end = tmr.now()
		end
	end

	return self
end
