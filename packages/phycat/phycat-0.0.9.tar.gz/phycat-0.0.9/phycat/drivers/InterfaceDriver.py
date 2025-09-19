
from .EmulatedMemory import EmulatedMemory
from cliify import commandParser, command
from phycat.protocol.phycatService import *
from polypacket.polyservice import PolyPacket 
from phycat.drivers.DeviceDriver import PhycatDeviceDriver

from phycat import PhycatSession

@commandParser(subparsers=['devices'])
class PhycatInterfaceDriver:
    def __init__(self, session : PhycatSession, handle ):
        self.handle = handle
        self.name = None 
        if session != None:
            self.name = session.getIfaceLabel(self.handle)
        self.type = None
        self.session : PhycatSession = session
        self.devices : list[PhycatDeviceDriver] = []
        self.pinLabels = {}

    def addDevice(self, device):
        device.interface = self
        self.devices.append(device)

    def send(self, msg):
        msg.handle = self.handle
        self.session.send(msg)
        pass

    def getPinLabel(self, handle):
        self.session.getPinLabel(handle)
    
    def getPinHandle(self, label):
        self.session.getPinHandle(label)

    def handleMessage(self, msg : PolyPacket):
        print(f"Message handler not implemented for {self.name}")
        pass

    def getCapabilities(self) -> PolyPacket:
        pass

