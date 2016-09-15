import machine

class DistanceSensor:

    def __init__(self, trigger, echo):
        self.lastHighTime = 0
    
        self.triggerPin = machine.Pin(0, machine.Pin.OUT)
        self.triggerPin.value(0)
        self.echoPin = Pin(4, Pin.IN)
        
    def Measure(self):
        self.triggerPin.value(1)
        #time.sleep(0.001)
        self.triggerPin.value(0)
        
        time = machine.time_pulse_us(self.echoPin, 1, 100000)
        dist = 165.7 * time * 3.28084 / 1000000
        #print("Dist: ", dist, " ft. Temp Timer: ", time)
        
        return dist
