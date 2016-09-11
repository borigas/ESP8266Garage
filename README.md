# GarageMqtt

Sensor and remote for garage door. Mounts on ceiling of garage and detects if the garage is open or closed and sends the status to an Mqtt relay. Also accepts messages from the relay to open and control the door.

###Photos:###
https://goo.gl/photos/TKTH1ud8kynhA8XG7

###Circuit Diagram:###
https://circuits.io/circuits/2474900-mqtt-garage-door-sensor

###Parts###

| Part        | Price | Notes                               |
|-------------------|-------|--------------------------------|
| Breadboard        | $1.60 |                                |
| ESP8266           | $4.70 |                                |
| US-100            | $2.20 | Similar to HC-SR04, but for 3v |
| 3v Relay             | $2.50 |                        |
| 330Ω resistor     |       |                                |
| 2n2222 transistor |       |                                |
| Total | $11      |                                |

###Notes###
- The amp is because the ESP8266 IO pins don't source enough current to trigger the relay. The 3v pin does though, so I use the current from that
