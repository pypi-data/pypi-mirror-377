

from phycat.protocol.phycatService import *
from polypacket.polyservice import PolyPacket , BasePacket
from phycat import PhycatSession

import logging

log = logging.getLogger(__name__)
    
class PhycatInterface:
    def __init__(self, session : PhycatSession, handle ):
        self.session : PhycatSession = session
        self.handle = None
        self.type = None 
        self.setHandle(handle)

    def setHandle(self, handle):
        self.handle = handle

        if handle is not None:
            self.type = handleType((handle >> 16) & 0xFFFF).name.lower()
            ifaceNum = handle & 0xFFFF
            self.name = f"{self.type}{ifaceNum}"


    def send(self, msg : BasePacket | PolyPacket, fields = {} ):
        self.session.send(msg, fields)


    def handleMessage(self, msg : PolyPacket) -> PolyPacket | None:
        log.warning(f"Message handler not implemented for {self.handle}")
        return None

    def getCapabilities(self) -> BasePacket | None:
        log.warning(f"Capabilities not implemented for {self.handle}")
        return None



        