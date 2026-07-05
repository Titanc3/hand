import network
import espnow
from machine import Pin, PWM, sleep

sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)
sta.disconnect()      # For ESP8266

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

exitPin = Pin(26, Pin.IN, Pin.PULL_UP) # connect to nearby gnd w/ button to kill process

a = Pin(15, Pin.OUT)
b = Pin(4, Pin.OUT)

while exitPin.value() == 1: # alternative to reset button
    a.value(0)
    b.value(1)
    print("A"+str(a.value()))
    print("B"+str(b.value()))
    
    sleep(50)
    
