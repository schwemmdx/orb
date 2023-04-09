
from time import sleep
from esp32 import raw_temperature

from machine import Timer,Pin

from server import BLEServer
from oled import OledDisplay


 



def convertFtoC(temp):
    return (temp-32)*5/9

oled = OledDisplay()
ble = BLEServer('orb-bl',oled)


tim = Timer(3)                              
wd_timer = Timer(2)


while not ble.conn:
    pass

def watchdog(tim):
    global oled
    ble.notify("Watchdog triggered\n")
    oled.display.fill(0)
    


tim.init(mode=Timer.PERIODIC,freq=0.05,callback=watchdog)      
     
#while True:
#     
#    temp = str(convertFtoC(raw_temperature()))
#    ble.notify(temp + ' °C\n')
#    sleep(10)