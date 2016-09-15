import machine
import time
import ubinascii
import ujson

from Relay import Relay
from DistanceSensor import DistanceSensor
from MqttHelper import MqttHelper
    
class MqttGarage:
    
    def __init__(self):
        trigger = 0
        echo = 4
        relayPin = 5
        serverAddress = "192.168.1.12"
        
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
        self.recentDistances = list()
        
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
                    self.ToggleDoor(True)
                elif currentMessage == closeMsg:
                    self.ToggleDoor(False)
            
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
        hasPublishExpired = lastPublishAge < 0 or lastPublishAge > 60 * 15 / 1.122833 # Clock isn't very accurate. Scale it back to real time
        
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
        checkCount = 5
        distances = list()
        
        for i in range(checkCount):
            distance = self.distanceSensor.Measure()
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