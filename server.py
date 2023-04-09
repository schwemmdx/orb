
import ubluetooth
from micropython import const
import machine
from oled import OledDisplay
import json
import os
import utime

_ADV_TYP_NAME = const(9)
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(2)
_FLAG_WRITE = const(8)
_FLAG_NOTIFY = const(16)


class Protocol():
    def __init__(self,server):
        self.ble_server = server
        self.cmds = {
            "ls": "lists internal filesystem",
            "mkdir": "creates folder",
            }
        self.props = {
            "log_interval": "Time Interval of Data Sampling"
            }
        self.actions = {
            "reset": "Hardware Reset",
            "log-start": "Starts Logging",
            "log-stop": "Stops Logging"
            }
    
    def rx_handler(self,cmd):
        self.ble_server.display.display.fill(0)
        self.ble_server.display.write_line("RX:",0)
        self.ble_server.display.write_line(cmd,1)
        cmd = cmd.lower()
        
        if cmd in ["cmd?","help","info"]:
            self.ble_server.notify("Basic Commands:\r\n")
            for key in self.cmds:
                self.ble_server.notify(key+": "+self.cmds[key]+"\r\n")
            self.ble_server.notify("Settings:\r\n")
            for key in self.props:
                self.ble_server.notify(key+": "+self.props[key]+"\r\n")
            self.ble_server.notify("Actions:\r\n")
            for key in self.actions:
                self.ble_server.notify(key+": "+self.actions[key]+"\r\n")
                
        elif "ls " in cmd:
            folder = cmd.split("ls ")[1]
            files = os.listdir(folder)
            if len(files) < 1:
                self.ble_server.notify("\r\n")
            for file in files:
                self.ble_server.notify(f"{file}\r\n")
        elif "mkdir" in cmd:
            folder = cmd.split("mkdir ")[1]
            try:
                os.mkdir(folder)
            except Exception as ex:
                self.ble_server.notify(ex)
            
        elif "=" in cmd:
            #we set paramters
            if "log_interval" in cmd:
                self.ble_server.notify("Under construction\r\n")
            else:
                self.ble_server.notify("Unknown command\r\n")
            
        elif "?" in cmd:
            #we get parameters
            if cmd == "ver?":
                 self.ble_server.notify("Server Ver: 0.1\nDisplay Drv: 0.1\nProtocol Ver: 0.1a\r\n")
            elif cmd =="idn?":
                self.ble_server.notify("idn: 0x0000001\r\n")
                
            elif cmd == "log_interval?":
                self.ble_server.notify("dt: 10s")
            elif cmd == "sysfiles?":
                files = os.listdir("./")
                for file in files:
                    self.ble_server.notify(f"{file}\r\n")
            else:
                self.ble_server.notify("Unknown command\r\n")
                
        elif "!"  in cmd:
            if cmd == "reset!":
                self.ble_server.notify("Undergoing reset\r\n")
                utime.sleep_ms(250)
                machine.reset()
            elif cmd == "log-start!":
                self.ble_server.notify("not implemented\r\n")
            elif cmd == "log-stop!":
                self.ble_server.notify("not implemented\r\n")
            else:
                self.ble_server.notify("Unknown command\r\n")
                
        else:
            self.ble_server.notify("Unknown command\r\n")
            


class BLEServer():

    def __init__(self, name,hw_display):
        
        self.name = name
        self.display = hw_display
        self.protocol = Protocol(self)
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()
        
        self.conn = False


    def ble_irq(self, event, data):
        
        if event == _IRQ_CENTRAL_CONNECT:
            self.display.write_line("Connection",0)
            self.display.write_line("from Central",1)
            self.display.write_line("sucessful",2)
            self.conn = True
        
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print('Central disconnected')
            self.conn = False
            self.advertiser()
            
        elif event == _IRQ_GATTS_WRITE:
            buffer = self.ble.gatts_read(self.rx)
            message = buffer.decode('UTF-8').strip("\r\n")
            self.protocol.rx_handler(message)
            
            


    def register(self):
        
        # Nordic UART Service (NUS)
        
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), _FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), _FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)


    def notify(self, data):
        
        self.ble.gatts_notify(0, self.tx, data)


    def advertiser(self):
        
        adv_data = b'\x02\x01\x06'
        name = bytes(self.name, 'UTF-8')
        adv_data = adv_data +  bytearray((len(name) + 1, _ADV_TYP_NAME)) + name
        self.ble.gap_advertise(200000, adv_data, connectable=True)   # 200 ms Adv_Antervall 
        self.display.write_line("Bluetooth",0)
        self.display.write_line("Advertising",1)

