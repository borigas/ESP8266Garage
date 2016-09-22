# GarageMqtt

Sensor and remote for garage door. Mounts on ceiling of garage and detects if the garage is open or closed and sends the status to an Mqtt relay. Also accepts messages from the relay to open and control the door.

###Photos:###
https://goo.gl/photos/TKTH1ud8kynhA8XG7

###Circuit Diagram:###
https://circuits.io/circuits/2474900-mqtt-garage-door-sensor

###Case Designs###
https://tinkercad.com/things/8l6zTLbaJ09

###Parts###

| Part        | Price |
|-------------------|-------|--------------------------------|
| [Breadboard](http://www.electrodragon.com/product/small-size-breadboard-layout-pcb/)        | $1.60 |
| [ESP8266](http://www.electrodragon.com/product/nodemcu-lua-amica-r2-esp8266-wifi-board/)           | $4.70 |
| [US-100 3v Distance Sensor](https://www.amazon.com/gp/product/B00LQEUFHC/ref=oh_aui_detailpage_o04_s00?ie=UTF8&psc=1)            | $2.20 |
| [JRC-21F 3v Relay](https://www.amazon.com/gp/product/B00LQEUFHC/ref=oh_aui_detailpage_o04_s00?ie=UTF8&psc=1)             | $2.50 
| 330Ω resistor     |       |
| 2n2222 transistor |       |
| PLA for case | $4 |
| Total | $15      |

###Notes###
- The amp is because the ESP8266 IO pins don't source enough current to trigger the relay. The 3v pin does though, so I use the current from that
