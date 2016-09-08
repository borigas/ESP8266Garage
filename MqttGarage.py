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
        self.Open()
        pass
    
    def Open(self):
        self.controlPin.value(0)
        
    def Close(self):
        self.controlPin.value(1)
        
        
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
        #print("Dist: ", dist, " ft. Temp Timer: ", time)
        
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

    def Subscribe(self, topic, callback):
        self.mqttClient.set_callback(callback)
        self.mqttClient.subscribe(topic)
        
    def CheckForMessage(self):
        self.mqttClient.check_msg()
    
    
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
        self.setTopic = self.baseTopic + "/set"
        
        self.mqttClient.Subscribe(self.setTopic, self.SubscribeCallback)
        
        self.timer = machine.Timer(0)
        
        self.distance = 0
        self.isOpen = False
        self.isCarPresent = False
        self.hasRun = False
        self.hasNewMessage = False
        self.lastPublish = 0
        self.lastSubscribe = 0
        
    def timerCallback(self, timer):
        isTimeLocked = False
        if self.lastSubscribe != 0:
            now = time.time()
            lastSubscribeAge = now - self.lastSubscribe
            # Lock for 1 min after receiving a message
            isTimeLocked = lastSubscribeAge < 60
        
        hadMessage = self.CheckMqttMessages(not isTimeLocked)
        if not isTimeLocked and not hadMessage:
            self.CheckDistance()
        
    def CheckMqttMessages(self, processMessages):
        self.mqttClient.CheckForMessage()
        hadMessage = self.hasNewMessage
        if hadMessage:
            self.hasNewMessage = False
            self.lastSubscribe = time.time()
            
            if processMessages:
                openMsg = b'open'
                closeMsg = b'close'
                currentMessage = self.lastMessage
                if currentMessage == openMsg:
                    self.OpenDoor()
                elif currentMessage == closeMsg:
                    self.CloseDoor()
            
        return hadMessage
    
        
    def SubscribeCallback(self, topic, msg):
        print("MsgReceived. Topic: ", topic, " Msg: ", msg)
        self.lastTopic = topic
        self.lastMessage = msg
        self.hasNewMessage = True
        
    def CheckDistance(self):
        distance = self.GetDistance()
        
        now = time.time()
        lastPublishAge = now - self.lastPublish
        
        isOpen = self.IsDoorOpen(distance)
        isCarPresent = self.IsCarPresent(distance)
        
        isValidReading = self.IsValidReading(distance)
        
        hasDoorOpenChanged = isOpen != self.isOpen
        hasCarStatusChanged = isCarPresent != self.isCarPresent
        hasDistanceChanged = abs(distance - self.distance) > 0.2
        hasPublishExpired = lastPublishAge > 60 * 60 # 1 hr
        
        #print("Dist:", distance, " HasRun:", self.hasRun, " IsValid:", isValidReading, " IsOpen:", isOpen, " CarPresent:", isCarPresent, " DoorChanged:", hasDoorOpenChanged, " CarChanged:", hasCarStatusChanged, " DistChanged:", hasDistanceChanged, " PubChanged:", hasPublishExpired, " PubAge:", lastPublishAge, " Now:", now, " Last:", self.lastPublish)
        
        if isValidReading and ((not self.hasRun) or hasDoorOpenChanged or hasCarStatusChanged or hasDistanceChanged or hasPublishExpired):
        
            self.distance = distance
            self.isOpen = isOpen
            self.isCarPresent = isCarPresent
            
            self.PublishStatus()
            
            self.lastPublish = now
            self.hasRun = True
            
    def GetDistance(self):
        distanceTolerance = 0.2
        checkCount = 7
        distances = list()
        
        for i in range(checkCount):
            distance = self.distanceSensor.Measure()
            if self.IsValidReading(distance):
                distances.append(distance)
                
        if len(distances) == 0:
            return 0
        else:
            first = distances[0]
            for dist in distances:
                if abs(first - dist) >= distanceTolerance:
                    return 0
            return max(distances)
        
            
    def PublishStatus(self):
        status = "closed"
        if self.isOpen:
            status = "open"
        
        dictionary = dict(
            Status = status,
            Distance = self.distance, 
            IsOpen = self.isOpen,
            IsCarPresent = self.isCarPresent,
            ClientId = self.clientId,
        )
        msg = ujson.dumps(dictionary)
        topic = self.baseTopic
        print(topic + ": " + msg)
        self.mqttClient.Publish(topic, msg)
            
    def IsDoorOpen(self, distance):
        return distance <= 4
        
    def IsCarPresent(self, distance):
        return distance <= 6
        
    def IsValidReading(self, distance):
        return 0.1 < distance < 25
            
    def OpenDoor(self):
        self.ToggleDoor(True)
        
    def CloseDoor(self):
        self.ToggleDoor(False)
            
    def ToggleDoor(self, desiredIsOpen):
        distance = self.GetDistance()
        
        expectedCurrentIsDoorUp = not desiredIsOpen
        
        if self.IsValidReading(distance) and self.IsDoorOpen(distance) == expectedCurrentIsDoorUp:
            self.relay.Close()
            time.sleep(0.1)
            self.relay.Open()
            
            self.isOpen = desiredIsOpen
            
            self.PublishStatus()
        
    def StartTimer(self):
        self.timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self.timerCallback)
        
    def StopTimer(self):
        self.timer.deinit()

    def Run():
        instance = MqttGarage()
        instance.StartTimer()
        return instance