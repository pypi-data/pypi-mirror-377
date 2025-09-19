from phycat.protocol.phycatService import *

from polypacket.polyservice import PolyService, PolyPacket

from phycat.interfaces import PhycatInterface

from phycat.PhycatSession import PhycatSession
from phycat.interfaces import *
from phycat.helpers.driver_helper import load_plugin_class, find_plugins_in_dir
import yaml
from importlib import resources
import os
import logging



log = logging.getLogger(__name__)

class PhycatServer(PhycatSession):
    def __init__(self, server_config = None, interface_dirs = []): 
        super().__init__()
        """
            Create a new PhycatServer object.

            connString: connection string to use to connect to the Phycat device.

            server_config: Configuration if running as server (i.e. acting as the Phycat device)
        
        """

        pkg_dir = resources.files('phycat')
        protocol_file = os.path.join(pkg_dir, 'protocol', 'poly', 'phycat.yml')

        self.service = PolyService(protocol_file)
        #self.service.silenceAll = True
        self.service.addHandler('default', self.handleMessage)

        self.interfaces:  dict[ int, PhycatInterface]  = {}


        self.interface_dirs = [os.path.join(pkg_dir, 'interfaces')]
        self.interface_dirs.extend(interface_dirs)

        #gather interface plugins 
        classes = find_plugins_in_dir(self.interface_dirs[0], PhycatInterface)
        self.interface_classes = { cls.__name__: cls for cls in classes }

        self.system = System()
        self.system.clockSpeed = 9999999
        self.system.portCount = 0
        self.system.interfaceCount = 0
        self.system.label = "PhycatServer"
        self.portLabels = ['A', 'B', 'C', 'D']
        if server_config is not None:
            self.initInterfaces(server_config)



    def start(self, connString: str):
        """
            Start the Phycat service with a connection string.

            Connection strings are of the form:

            serial:/dev/ttyS0:115200-8N1
            tcp:8020 (listen on port 8020)
            ws:8020 (start websocket server on port 8020)
            tcp:localhost:8020 (connect to localhost on port 8020)

        """


        log.info(f"Listening with {connString}")
        self.service.connect(connString)
        

    def close(self):
        self.service.close()

    def getNextIfaceHandle(self, type: str | int):

        nextId = 0
        if isinstance(type, str):
            type = handleType[type.upper()].value

        for iface in self.interfaces:
            if (iface.handle >> 16) == type:
                id = iface.handle & 0xFFFF
                if id >= nextId:
                    nextId = id + 1

        return (type << 16) | nextId
    

    def addInterface(self, iface: PhycatInterface):
        if iface.handle is None:
            iface.handle = self.getNextIfaceHandle(iface.type)

        self.interfaces[iface.handle] = iface
        self.system.interfaceCount = len(self.interfaces)
        log.info(f"Added interface {iface.name} with handle {hex(iface.handle)}")

    def initInterfaces(self, config):


        if( not os.path.exists(config) ):
            #check for default configs in the phycat package
            default_config_dir = os.path.join(resources.files('phycat'),'configs')
            if not config.endswith('.yml'):
                config = config + '.yml'
            
            if os.path.exists( os.path.join(default_config_dir,  config) ):
                config = os.path.join(default_config_dir, config)
            else:
                print(f"Could not find server config {config}")
                return
        

        with open(config, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        
            
            if 'interfaces' in config:

                for ifaceConfig in config['interfaces']:
                    if 'class' not in ifaceConfig:
                        log.warning(f"Interface config missing 'class' field, skipping: {ifaceConfig}")
                        continue

                    if 'type' not in ifaceConfig:
                        log.warning(f"Interface config missing 'type' field, defaulting to 'dummy': {ifaceConfig}")
                        continue
                    
                    ifaceType = ifaceConfig['type']
                    #iF the class is known and loaded from one of the interface dirs, use it
                    if ifaceConfig['class'] in self.interface_classes:
                        ifaceClass = self.interface_classes[ifaceConfig['class']]
                    else:
                        #try to load it as a plugin
                        try:
                            ifaceClass = load_plugin_class(ifaceConfig['class'], self.interface_dirs)
                        except Exception as e:
                            log.error(f"Failed to load interface class {ifaceConfig['class']}: {e}")
                            continue

                    newHandle = self.getNextIfaceHandle(ifaceType)
                    params = ifaceConfig.get('parameters', {})
                    newIface = ifaceClass(session = self, handle = newHandle, **params)

                    self.addInterface(newIface)
 

        self.system.interfaceCount = len(self.interfaces)
    

    
    def handleMessage(self, service, ppPacket : PolyPacket):

        type = ppPacket.typeId 
        packetType = ppPacket.desc.name.lower()
        req : BasePacket = PolyPacketToPhycatPacket(ppPacket)

        #print(f"Received message {ppPacket.toJSON()}")



        if packetType == 'request':
            if req.requestType == requestType.SYSTEM:
                log.info("System requested")
                return self.system
            

            elif req.requestType == requestType.PORT:
                if req.index is not None and req.index < len(self.portLabels):
                    port = Port()
                    port.index = req.index
                    port.label = self.portLabels[req.index]
                    return port
                else:
                    log.warning(f"Port request for unknown index {req.index}")
            elif req.requestType == requestType.CAPABILITIES:
                caps = None
                if req.handle is not None and req.handle in self.interfaces:
                    caps = self.interfaces[req.handle].getCapabilities()
                    caps.handle = req.handle
                elif req.index is not None: 
                    ifaceList = list(self.interfaces.values())
                    if req.index < len(ifaceList):
                        caps = ifaceList[req.index].getCapabilities()
                        caps.handle = ifaceList[req.index].handle
                if caps is not None:
                    return caps
                else:
                    log.warning(f"Capabilities request for unknown handle {req.handle} or index {req.index}")
        
        #if packet has handle 
        elif ppPacket.hasField('handle') and req.handle in self.interfaces:
            resp = self.interfaces[req.handle].handleMessage(req)
            if resp is not None:
                return resp
        

        
        
        
        return None


    