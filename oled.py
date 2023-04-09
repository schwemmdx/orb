from ssd1306 import SSD1306_I2C

from machine import Pin,I2C

import utime

class OledDisplay():
    def __init__(self, i2cId=1,scl=Pin(21),sda=Pin(22),wPx = 128,hPx=32):
        self.i2c = I2C(1,scl=scl,sda=sda)
        self.display = SSD1306_I2C(wPx,hPx,self.i2c)
        self.__char_height =10
        self.linePixels = [
            1,9,20
        ]
        self.display.fill(0)
    
    def write_line(self,msg,lineId):
        self.display.fill_rect(0, lineId*self.__char_height, 128, lineId*self.__char_height+self.__char_height, 0)
        self.display.text(msg,0,lineId*self.__char_height)
        self.display.show()


#doenat work!
    def write(self,msg):
        self.display.fill(0)
        #lines = msg.split('\n')
        i=0
        for line in msg:
            self.write_line(line,i*self.__char_height)
            utime.sleep_ms(250)
            #print(line+" "+str(i))
            i+=1
            
    
    def error(self,errorMsg,errCode=-1):
        self.write_line("[ERROR] " +errCode,0)
        self.write_line(errorMsg,1)
        
    def info(self,msg,periph=""):
        self.write_line("[INFO] " +periph,0)
        self.write_line(msg,1)
      

