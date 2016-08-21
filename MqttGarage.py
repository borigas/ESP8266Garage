import machine
from machine import Pin
import time
from simple import MQTTClient
import ubinascii
import ujson

# WatchDog timer to restart device: http://docs.micropython.org/en/latest/esp8266/library/machine.WDT.html


class Relay:

    def __init__(self, pin, initialValue=0):
        self.controlPin = Pin(pin, Pin.OUT)
        self.controlPin.value(0)
        pass
    
    def Open(self):
        self.controlPin.value(1)
        
    def Close(self):
        self.controlPin.value(0)
        
        
class DistanceSensor:

    def pinCallback(self, p):
        us = time.ticks_us()
        value = p.value()
        #print('Pin Change', p, " value: ", value, " us: ", us)
        
        if(value == 1):
            self.lastHighTime = us
        else:
            diff = time.ticks_diff(self.lastHighTime, us)
            dist = 165.7 * diff / 1000000
            self.lastHighTime = 0
            #self.measureCallback(dist, diff)
            
    def __init__(self, trigger, echo):
        self.lastHighTime = 0
    
        self.triggerPin = machine.Pin(0, machine.Pin.OUT)
        self.triggerPin.value(0)
        self.echoPin = Pin(4, Pin.IN)
        
        #self.echoPin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.pinCallback)
        
    def Measure(self):
        #print("Triggering ", self.triggerPin, " Listening ", self.echoPin)
        self.triggerPin.value(1)
        #time.sleep(0.001)
        self.triggerPin.value(0)
        
        time = machine.time_pulse_us(self.echoPin, 1, 100000)
        dist = 165.7 * time * 3.28084 / 1000000
        print("Dist: ", dist, " ft. Temp Timer: ", time)
        
        return dist
        

class MqttHelper:
    
    def __init__(self, serverAddress, clientId):
    #, subscribeTopics, subscribeCallback):
        self.mqttClient = MQTTClient(clientId, serverAddress)
        self.mqttClient.connect()
        
#        self.mqttClient.set_callback(sub_cb)
#        
#        self.mqttClient.connect()
#        
#        self.mqttClient.subscribe(b"foo_topic")
#        
#        for topic in subscribeTopics:
#            binaryTopic = ubinascii.a2b_base64(topic)
#            self.mqttClient.subscribe(binaryTopic)
            
        
    def Publish(self, topic, message):
        # TODO Take topic and data as params
        # TODO Then need to convert to binary for publish. Probably using ubinascii.a2b_base64(data)
        self.mqttClient.publish(topic, message)
        
    def CheckForMessage(self):
        self.mqttClient.chech_msg()
    
    
class MqttGarage:
    
    def __init__(self):
        trigger = 0
        echo = 4
        relayPin = 5
        serverAddress = "192.168.1.11"
        
        self.distanceSensor = DistanceSensor(trigger, echo)
        
        self.relay = Relay(relayPin)
        
        self.clientId = str(ubinascii.hexlify(machine.unique_id()), "utf-8")
        self.mqttClient = MqttHelper(serverAddress, self.clientId)
        
        self.baseTopic = "home/garage/door/" + self.clientId
        
        self.timer = machine.Timer(0)
        
        self.distance = 0
        self.isOpen = false
        self.isCarPresent = false
        self.hasRun = false
        self.lastPublishMs = 0
        
    def timerCallback(self, timer):
        self.CheckDistance()
        
    def CheckDistance(self):
        distance = self.distanceSensor.Measure()
        
        lastCheckMs = utime.ticks_ms()
        lastPublishAgeMs = utime.ticks_diff(lastCheckMs, self.lastPublishMs)
        
        isOpen = self.IsDoorOpen(distance)
        isCarPresent = self.IsCarPresent(distance)
        
        isValidReading = self.IsValidReading(distance)
        
        hasDoorOpenChanged = isOpen != self.isOpen
        hasCarStatusChanged = isCarPresent != self.isCarPresent
        hasDistanceChanged = abs(distance - self.distance) > 0.2
        hasPublishExpired = lastPublishAgeMs > 60 * 60 * 1000 # 1 hr
        
        if isValidReading and ((not hasRun) or hasDoorChanged or hasCarStatusChanged or hasDistanceChanged or hasPublishExpired):
        
            self.distance = distance
            self.isOpen = isOpen
            self.isCarPresent = isCarPresent
            
            status = "closed"
            if isOpen:
                status = "open"
            
            dictionary = dict(
                Status = status,
                Distance = distance, 
                IsOpen = isOpen,
                IsCarPresent = isCarPresent,
                ClientId = self.clientId,
            )
            msg = ujson.dumps(dictionary)
            topic = self.baseTopic + "/status"
            print(topic + ": " + msg)
            self.mqttClient.Publish(topic, msg)
            
    def IsDoorOpen(self, distance):
        return distance > 3
        
    def IsCarPresent(self, distance):
        return distance <= 6
        
    def IsValidReading(self, distance):
        return 0.5 < distance < 25
            
    def OpenDoor(self):
        self.ToggleDoor(false)
        
    def CloseDoor(self):
        self.ToggleDoor(true)
            
    def ToggleDoor(self, expectedCurrentIsDoorUp):
        distance = self.distanceSensor.Measure()
        
        if self.IsValidReading(distance) and self.IsDoorOpen(distance) == expectedCurrentIsDoorUp:
            self.relay.close()
            utime.sleep(0.01)
            self.relay.open()
        
    def StartTimer(self):
        self.timer.init(period=5000, mode=machine.Timer.PERIODIC, callback=self.timerCallback)
        
    def StopTimer(self):
        self.timer.deinit()