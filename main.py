import network
import espnow
from machine import Pin, ADC, sleep, PWM
import asyncio

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
  

pList = [p1, p2, p3] # add peers here
pIndex = 0 # index to use when connecting to peers
espn.add_peer(pList[pIndex])


right = Pin(19, Pin.IN, Pin.PULL_UP) # left arrow button
left = Pin(21, Pin.IN, Pin.PULL_UP) # right arrow button

lr = PWM(Pin(4, 10000)) # light (color) red
lg = PWM(Pin(16, 10000))
lb = PWM(Pin(17, 10000))

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
bL = 0
bR = 0
connection = "searching"

async def ledColor(state):
    lr.init(duty=1023)
    lg.init(duty=1023)
    lb.init(duty=1023)
    
    if state == "connected":
        brightness = 1023-600
    else: # hovering in menu
        brightness = 1023-100
    
    if pIndex == 0:
        lr.init(duty=brightness)
    elif pIndex == 1:
        lg.init(duty=brightness)
    else:
        lb.init(duty=brightness)
    await asyncio.sleep_ms(25)
        
async def btnPoll(pL):
    bL = 1-left.value() # [set up vars per 50ms frame]
    bR = 1-right.value() # invert values so 1 = activated instead of off
    global pIndex
    global connection
    global bLDisable
    global bRDisable
    if bL:
        if bLDisable == 0:
            connection = "connected"
            bLDisable = 5
        else:
            bLDisable -= 1
    
    if bR:
        if bRDisable == 0:
            connection = "searching"
            espn.del_peer(pL[pIndex])
            pIndex -= 2
            pIndex = pIndex % len(pL)
            espn.add_peer(pL[pIndex])
            bRDisable = 5
        else:
            bRDisable -= 1
    print(pIndex)
    await asyncio.sleep_ms(75)

async def sendData(a, b, c, d, conn, pL, pI):
    if conn == "connected":
            espn.send(pL[pI], f"{a}:{b}:{c}:{d}") # send usable data
    await asyncio.sleep_ms(50)

async def main():
    while 1:
        A = clamp(a.read()/3500, 0, 1) # convert to % flex
        B = clamp(b.read()/3500, 0, 1)
        C = clamp(c.read()/3500, 0, 1)
        D = clamp(d.read()/3500, 0, 1)
        bL = 1-left.value() # [set up vars per 50ms frame]
        bR = 1-right.value() # invert values so 1 = activated instead of off

        print("Left: "+str(bL))
        print("Right: "+str(bR))
        print(pIndex)
        print(connection)
        print("\n\n\n")
        
        asyncio.create_task(btnPoll(pList))
        asyncio.create_task(sendData(A, B, C, D, connection, pList, pIndex))
        asyncio.create_task(ledColor(connection))
        
        exitNum = exitNum+1 if bL+bR == 2 else 0

        if exitNum >= 100: #lazy? yes | works? yes
            break
        
        
        await asyncio.sleep_ms(20)
    

asyncio.run(main())

            
        
