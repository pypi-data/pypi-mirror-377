from phycat.protocol.phycatService import *

from polypacket.polyservice import PolyService, PolyPacket

from importlib import resources
import os
import logging

log = logging.getLogger(__name__)


class PhycatSession:
    def __init__(self): 
        
        pkg_dir = resources.files('phycat')
        protocol_file = os.path.join(pkg_dir, 'protocol', 'poly', 'phycat.yml')


        self.service = PolyService(protocol_file)
    

    def connect(self, connString: str):
        """
            Connect to a Phycat device using the specified connection string.

            Connection strings are of the form:

            serial:/dev/ttyS0:115200-8N1
            tcp:8020 (listen on port 8020)
            tcp:localhost:8020 (connect to localhost on port 8020)

        """

        log.info(f"Connecting to {connString}")
        self.service.connect(connString)
        self.discover()
        # if self.client.connected:
        #     self.startDiscovery()

    def close(self):
        self.service.close()

    
    def send(self, msg : BasePacket | PolyPacket, fields = {} ):

        self.service.sendPacket(msg, fields)

    def getIfaceLabel(self, handle):

        ifaceType = handleType(handle >> 16).name.lower()

        if ifaceType == "gpio":
            pinLabel = self.getPinLabel(handle)
            return f"{ifaceType}{pinLabel}"
        else:

            ifaceNum = handle & 0xFFFF
            return f"{ifaceType}{ifaceNum}"

    def getIfaceHandle(self, label):

        try:

            if label in self.interfaces:
                return self.interfaces[label].handle
            else:
                if label.startswith("gpio"):
                    pinHandle = self.getPinHandle(label[4:])
                    return handleType.GPIO.value << 16 | pinHandle
                elif label.startswith("i2c"):
                    return handleType.I2C.value << 16 | int(label[3:])
                elif label.startswith("uart"):
                    return handleType.UART.value << 16 | int(label[4:])
                else:
                    #TODO support more interfaces
                    print(f"Invalid interface label {label}")
                    return None
        
        except:
            print(f"Invalid interface label {label}")
            return None
    
    
    def getPinHandle(self, label):
        """ Converts a pin label to a uint32 handle.

        example: 

            portLabels = { 0x01: "GPIOA", 0x02: "GPIOB" }

            getPinHandleFromLabel("GPIOA4") -> 0x00010004
        
        """

        port = None 
        pin = None

        for handle, lbl in self.portLabels.items():
            if label.startswith(lbl):
                port = handle
                pin = int(label[len(lbl):])

                return port << 8 | (pin & 0xFF)
                break
                
        return None
    
    def getPinLabel(self, handle):
        port = (handle >> 8) & 0xFF
        pin = handle & 0xFF

        return self.portLabels[port] + str(pin)