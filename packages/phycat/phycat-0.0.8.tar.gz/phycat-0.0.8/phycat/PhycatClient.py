from phycat.protocol.phycatService import *

from polypacket.polyservice import PolyService, PolyPacket
from phycat.PhycatSession import PhycatSession

from phycat.drivers import *

from cliify import commandParser, command

from phycat.helpers.driver_helper import load_plugin_class
import logging
from termcolor import colored

log = logging.getLogger(__name__)


class SystemInfo:
    def __init__(self):
        self.name = ""
        self.portCount = 0
        self.interfaceCount = 0
        self.clockSpeed = 0


class DiscoveryState:
    def __init__(self):
        self.state = None
        self.index = 0

@commandParser(subparsers=['interfaces'], allow_eval=True)
class PhycatClient(PhycatSession):
    def __init__(self): 
        super().__init__()
        """
            Create a new PhycatSession object.

            connString: connection string to use to connect to the Phycat device.

            server_config: Configuration if running as server (i.e. acting as the Phycat device)
        
        """


        #self.service.silenceAll = True
        self.service.addHandler('default', self._handleMessage)
        #self.service.addHandler()

        


        self.portLabels: dict = {}
        self.interfaces: dict[ str, PhycatInterfaceDriver ] = {}


        #Default handlers for messages
        self.message_handler = self.handleMessage
        self.discovery_complete_handler = self.handleDiscoveryComplete

        #Track state of session
        self.system = SystemInfo()
        self.discoState = DiscoveryState()



    @command(completions={'path': ['$nodes','!help']})
    def help(self,path: str):
        strHelp = self.getHelp(path)

    @command
    def connect(self, connString: str):
        super().connect(connString)
        

    @command()
    def test(self):
        print("Test command")
        log.error("Test error")
        log.info("Test info")
        log.debug("Test debug")

    @command(completions={'path': ['$nodes']})
    def ls(self, path = '/'):
        
        if path == '/':
            print(f"{self.interfaces.keys()}")
   

    @command
    def discover(self):
        self.startDiscovery()    

    def startDiscovery(self):
        self.sendRequest(requestType.SYSTEM)
        self.discoState.state = 'system'
        self.discoState.index = 0

    def sendRequest(self, type, handle = None, index = None):

        packet = Request()
        packet.requestType = type

        if handle is not None:
            packet.handle = handle
        
        if index is not None:
            packet.index = index

        self.send(packet)


    def print(self, message):
        print(message)

    



    def addInterface(self, iface: PhycatInterfaceDriver):

        if iface.name in self.interfaces:
            print(f"Interface {iface.name} already exists")
            return
        else:
            self.interfaces[iface.name] = iface

    

    def _handleMessage(self, service, ppPacket : PolyPacket):

        self.message_handler(service, ppPacket )
            

    
    def handleMessage(self, service, ppPacket : PolyPacket):

        type = ppPacket.typeId 
        packetType = ppPacket.desc.name.lower()
        req : BasePacket = ppPacket.toBasePacket()

        log.debug(f"<<< {ppPacket.toJSON()}")


        if packetType == "port":
            self.portLabels[self.discoState.index] = req.label
            self.discoState.index += 1
            if self.discoState.index < self.system.portCount:
                self.sendRequest(requestType.PORT, index=self.discoState.index)
            else:
                self.discoState.state = 'interfaces'
                self.discoState.index = 0
                self.sendRequest(requestType.CAPABILITIES, index=0)
            
            return
        elif packetType == "system":
            self.system.name = req.label
            self.system.portCount = req.portCount
            self.system.interfaceCount = req.interfaceCount
            self.system.clockSpeed = req.clockSpeed

            if self.system.portCount > 0:
                self.discoState.state = 'ports'
                self.discoState.index = 0
                self.sendRequest(requestType.PORT, index=0)
            else:
                self.discoState.state = 'interfaces'
                self.discoState.index = 0
                self.sendRequest(requestType.CAPABILITIES, index=0)

            return


        elif packetType.endswith('capabilities'):
            hType = req.handle >> 16


            if hType == handleType.UART:
                iface = UartInterface(self, req.handle, req)
                self.addInterface(iface)
            elif hType == handleType.I2C:
                iface = I2cInterface(self, req.handle, req)
                self.addInterface(iface)
            

            self.discoState.index += 1
            if self.discoState.index < self.system.interfaceCount:
                self.sendRequest(requestType.CAPABILITIES, index=self.discoState.index)
            else:
                self.discoState.state = None
                self.discoState.index = 0
                self.discovery_complete_handler()
        elif packetType.endswith('data'):
            hType = req.handle >> 16
            if hType == handleType.UART:
                iface = self.interfaces.get(self.getIfaceLabel(req.handle), None)
                if iface:
                    iface.handleMessage(ppPacket)
            elif hType == handleType.I2C:
                iface = self.interfaces.get(self.getIfaceLabel(req.handle), None)
                if iface:
                    iface.handleMessage(ppPacket)
            else:
                print(f"Unhandled data packet for handle {req.handle} of type {hType}")
        elif packetType == "status":
            if req.status == 0:
                print(colored(f"OK", 'green'))
            else:
                print(colored(f"Error: {req.status}", 'red'))
        else:
            print(f" <<< {ppPacket.toJSON()}")

        
        
        
        return None


    def handlePortLabel(self, msg):
        
        self.portLabels[msg.handle] = msg.label

    def handleDiscoveryComplete(self):

        info = "Discovery complete\n"

        if len(self.portLabels.items()) > 0:
            info += "Port labels:\n"

            for handle, label in self.portLabels.items():
                info += f"  {handle}: {label}\n"

        info += "Interfaces:\n"
        for name, iface in self.interfaces.items():
            info += f"  {name}\n"

        print(info)



    