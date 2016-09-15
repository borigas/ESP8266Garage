import machine

class DistanceSensor:

    def __init__(self, trigger, echo):
        self.lastHighTime = 0
    
        self.triggerPin = machine.Pin(0, machine.Pin.OUT)
        self.triggerPin.value(0)
        self.echoPin = machine.Pin(4, machine.Pin.IN)
        self.recentDistances = list()
        
    def Measure(self):
        self.triggerPin.value(1)
        #time.sleep(0.001)
        self.triggerPin.value(0)
        
        time = machine.time_pulse_us(self.echoPin, 1, 100000)
        dist = 165.7 * time * 3.28084 / 1000000
        #print("Dist: ", dist, " ft. Temp Timer: ", time)
        
        return dist
            
    def SmoothedMeasure(self):
        distanceTolerance = 0.2
        checkCount = 5
        distances = list()
        
        for i in range(checkCount):
            distance = self.Measure()
            if self.IsValidReading(distance):
                distances.append(distance)
        
        currentMeasurement = 0
        if len(distances) != 0:
            currentMeasurement = max(distances)
            self.recentDistances.append(currentMeasurement)
            if len(self.recentDistances) > checkCount:
                self.recentDistances.pop(0)
        
            firstNum = self.recentDistances[0]
            for num in self.recentDistances:
                if abs(firstNum - num) > distanceTolerance:
                    return 0
            
        return currentMeasurement
        
    def IsValidReading(self, distance):
        return 0.1 < distance < 25
            
    def IsDoorOpen(self, distance):
        return distance <= 4
