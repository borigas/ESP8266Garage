import simple
import robust

class MyTemp:

    def Publish(self):
        print("Main")
        server = "192.168.1.11"
        c = simple.MQTTClient("test_client", server)
        c.connect()
        c.publish(b"foo_topic", b"hello")
        c.disconnect()
        print("done")

'''
from machine import Timer

tim = Timer(0)
tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t:count())


class Temp:

    password = "temppass"

    def Callback(self, p):
        us = time.ticks_us()
        value = p.value()
        print('Pin Change', p, " value: ", value, " us: ", us, " self: ", self)
        
        if(value == 1):
            self.lastHighTime = us
        else:
            #diff = time.ticks_diff(self.lastHighTime, us)
            diff = us - self.lastHighTime
            dist = 165.7 * diff / 1000000
            print('Time Diff: ', diff, 'Dist: ', dist)
            self.lastHighTime = 0
            
        print("Callback done")
            
    def __init__(self):
        self.lastHighTime = 0
    
        self.triggerPin = Pin(4, Pin.OUT)
        self.triggerPin.value(0)
        self.echoPin = Pin(5, Pin.IN)
        
        self.echoPin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.Callback)
        
    def Trigger(self):
        self.triggerPin.value(1)
        time.sleep(0.001)
        self.triggerPin.value(0)
'''