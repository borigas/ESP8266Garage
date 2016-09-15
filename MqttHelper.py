
from simple import MQTTClient

class MqttHelper:
    
    def __init__(self, serverAddress, clientId):
        self.mqttClient = MQTTClient(clientId, serverAddress)
        self.mqttClient.connect()
            
    def Publish(self, topic, message):
        self.mqttClient.publish(topic, message)

    def Subscribe(self, topic, callback):
        self.mqttClient.set_callback(callback)
        self.mqttClient.subscribe(topic)
        
    def CheckForMessage(self):
        self.mqttClient.check_msg()
    