-- https://github.com/nodemcu/nodemcu-firmware/wiki/nodemcu_api_en
print("Starting")
-- One time ESP Setup --

-- Blink using timer alarm --

timerId = 0 -- we have seven timers! 0..6
dly = 500 -- milliseconds
ledPin = 2 -- 3=GPIO00, 4=GPIO2
gpio.mode(ledPin,gpio.OUTPUT)
ledState = 0
tmr.alarm( timerId, dly, 1, function() 
  ledState = 1 - ledState;
  gpio.write(ledPin, ledState)
--  print("Toggle LED")--
end)


do
  local pin, pulse1, du, now, trig = 1, 0, 0, tmr.now, gpio.trig
  gpio.mode(pin,gpio.INT)
  local function pin1cb(level)
    local pulse2 = now()
    print( level, pulse2 - pulse1 )
    pulse1 = pulse2
--    trig(pin, level == gpio.HIGH  and "down" or "up")--
  end
  trig(pin, "both", pin1cb)
end


print("Done")