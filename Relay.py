from machine import Pin

class Relay:

    def __init__(self, pin, initialValue=0):
        self.controlPin = Pin(pin, Pin.OUT)
        self.Open()
        pass
    
    def Open(self):
        self.controlPin.value(0)
        
    def Close(self):
        self.controlPin.value(1)