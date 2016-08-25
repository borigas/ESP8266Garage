from MqttGarage import MqttGarage
import time

print("Sleeping so network can connect")
time.sleep(15)

print("Starting")

garage = MqttGarage.Run()

print("Started")