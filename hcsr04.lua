https://github.com/sza2/node_hcsr04

hcsr04 = {};

function hcsr04.init(pin_trig, pin_echo, average)
	local self = {}
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

	function self.measure()
        print("Measuring")
		gpio.trig(self.echo, "up", self.echo_cb)
		gpio.write(self.trig, gpio.HIGH)
		tmr.delay(100)
		gpio.write(self.trig, gpio.LOW)
		tmr.delay(100000)
		if (self.time_end - self.time_start) < 0 then
			return -1
		end
        print(self.time_end - self.time_start)
        print("Measured")
		return (self.time_end - self.time_start) / 5800
	end

	function self.measure_avg()
		if self.measure() < 0 then  -- drop the first sample
			return -1 -- if the first sample is invalid, return -1
		end
		avg = 0
		for cnt = 1, self.average do
			distance = self.measure()
			if distance < 0 then
				return -1 -- return -1 if any of the meas fails
			end
			avg = avg + distance
			tmr.delay(30000)
		end
		return avg / self.average
	end

	return self
end
