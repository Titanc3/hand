import network
import espnow
from machine import Pin, ADC, sleep

def clamp(n, minn, maxn): # generic func
    return max(min(maxn, n), minn)

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.WLAN.IF_STA)  # Or network.WLAN.IF_AP
sta.active(True)
sta.disconnect()      # For ESP8266

espn = espnow.ESPNow() # prepare wireless comms
espn.active(True)
p1 = b'0v\xf5\xa6Mh'   # MAC address of peers' wifi interface
p2 = b'0v\xf5\xa6Mh'
p3 = b'0v\xf5\xa6Mh'
p4 = b'0v\xf5\xa6Mh'
  

pList = [p1, p2, p3, p4] # add peers here
pIndex = 0 # index to use when connecting to peers
espn.add_peer(pList[pIndex])


left = Pin(19, Pin.IN, Pin.PULL_UP) # left arrow button
right = Pin(21, Pin.IN, Pin.PULL_UP) # right arrow button

led = Pin(15, Pin.OUT)

a = ADC(33) #finger pos left->right a=pinky
b = ADC(32) # ring finger
c = ADC(35) # middle finger 
d = ADC(34) # index finger
a.atten(ADC.ATTN_11DB)
b.atten(ADC.ATTN_11DB)
c.atten(ADC.ATTN_11DB)
d.atten(ADC.ATTN_11DB)

exitNum = 0
bLDisable = 0 # debounce
bRDisable = 0

while 1:
    bL = 1-left.value() # [set up vars per 50ms frame]
    bR = 1-right.value() # invert values so 1 = activated instead of off
    A = clamp(a.read()/3500, 0, 1) # convert to % flex
    B = clamp(b.read()/3500, 0, 1)
    C = clamp(c.read()/3500, 0, 1)
    D = clamp(d.read()/3500, 0, 1)

    print("Left: "+str(bL))
    print("Right: "+str(bR))
    print(f"{A}\n{B}\n{C}\n{D}")
    print(pIndex)
    
    if bL:
        if bLDisable == 0:
            espn.del_peer(pList[pIndex]) # del prev
            bLDisable = 5
            pIndex -= 1
            espn.add_peer(pList[pIndex]) # add new
        else:
            bLDisable -= 1
    
    if bR:
        if bRDisable == 0:
            espn.del_peer(pList[pIndex])
            bRDisable = 5
            pIndex += 1
            espn.add_peer(pList[pIndex])
        else:
            bRDisable -= 1
    
    exitNum = exitNum+1 if bL+bR == 2 else 0

    if exitNum >= 100: #lazy? yes | works? yes
        break
    
    espn.send(pList[pIndex], f"{A}:{B}:{C}:{D}") # send usable data

#pLowerPWR = machine.Pin(21, machine.Pin.OUT) # init bottom servo
#pLowerPWR.value(1) # applies to a pnp, so it's disabled
#pLowerPWM = machine.PWM(22, freq=50, duty_u16=4915)
#lowerPos = 90

            
        
