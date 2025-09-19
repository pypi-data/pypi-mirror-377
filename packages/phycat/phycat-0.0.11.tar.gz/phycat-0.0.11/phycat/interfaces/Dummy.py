from phycat.interfaces import PhycatInterface
from phycat.protocol import *
from polypacket.polyservice import  PolyPacket
import logging

log = logging.getLogger(__name__)

class DummyInterface(PhycatInterface):
    def __init__(self, session, handle, parameters = {}):
        super().__init__(session, handle)


    def getCapabilities(self):
        
        if self.type == 'uart':
            caps = UartCapabilities()
            caps.max_baud_rate = 9999999
        elif self.type == 'i2c':
            caps = I2cCapabilities()    
            caps.max_speed = 400000
            caps.i2cFlags = i2cFlags.MASTER | i2cFlags.SLAVE | i2cFlags.PROMISCUOUS | i2cFlags.PULL_UPS 
        else:
            log.warning(f"Unknown dummy interface type {self.type}, returning empty capabilities")

        return caps



    def handleMessage(self, msg : PolyPacket):

        if isinstance(msg, Request):
            if msg.requestType == requestType.CAPABILITIES:
                caps = self.getCapabilities()
                caps.handle = self.handle
                self.session.send(caps)
        else:

            log.info(f"Dummy[{self.name}] received message: {msg.toJSON()}")


