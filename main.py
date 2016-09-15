from MqttGarage import MqttGarage
import time

print("Sleeping so network can connect")
time.sleep(15)

print("Starting")

try:
    garage = MqttGarage()
    garage.StartTimer()
    print("Started")
finally:
    import webrepl
    webrepl.start()