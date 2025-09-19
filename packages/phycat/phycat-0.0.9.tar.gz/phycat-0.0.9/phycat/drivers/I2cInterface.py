from phycat.drivers import PhycatInterfaceDriver
from phycat.protocol.phycatService import *
from polypacket.polyservice import PolyPacket 
from cliify import commandParser, command



@commandParser
class I2cInterface(PhycatInterfaceDriver):
    def __init__(self, session, handle, capabilities : I2cCapabilities = None):
        super().__init__(session, handle)


        self.capabilities: I2cCapabilities = capabilities
        self.cfg : I2cConfig = None

        

    @command(completions={'role': ['master', 'slave'], 'speed': [100000, 400000, 1000000]})
    def config(self, role : str = None, speed=100000):
        """
            Configure the I2C interface.

            args:
            
            role: The role of the I2C interface. Can be 'master' or 'slave'
            speed: The clock speed of the I2C interface. Default is 100000
        """

        cfg = I2cConfig()
        cfg.i2cFlags = 0

        if role.lower() == 'master':
            cfg.i2cFlags |= i2cFlags.MASTER

        if speed is not None:
            cfg.clockSpeed = speed


        print(f"Configuring I2C interface {self.handle} with {cfg}")

        self.configure(cfg)

    def configure(self, config : I2cConfig):


        self.config = config
        self.send( config )

    @command
    def write(self, address, data):
        """
            Write data to an I2C device.

            args:

            address: The address of the I2C device
            data: The data to write to the device

        """
        msg = I2cData
        msg.i2cOperation = i2cOperation.WRITE
        msg.handle = self.handle
        msg.address = address
        msg.data = data

        self.send(msg)

    @command
    def read(self, address, length):
        msg = I2cData()
        msg.handle = self.handle
        msg.i2cOperation = i2cOperation.READ
        msg.address = address
        msg.size = length

        self.send(msg)
    
    # @command
    # def scan(self, start=0x00, end=0x7F):
    #     msg = I2cData
    #     msg.handle = self.handle
    #     msg.operation = i2cOperation.SCAN
    #     msg.address = start
    #     msg.length = (end - start) + 1


    #     self.session.send(msg)

    @command
    def readMem(self, address, mem_address, length, addr_size =1):

        msg = I2cData()
        msg.handle = self.handle
        msg.i2cOperation = i2cOperation.READ
        msg.address = address
        msg.size = length
        msg.memAddr = mem_address
        msg.memAddrSize = addr_size

        self.send(msg)

    @command
    def writeMem(self, address, mem_address, data, addr_size = 1):
        
        msg = I2cData()
        msg.handle = self.handle
        msg.i2cOperation = i2cOperation.WRITE
        msg.address = address
        msg.data = data
        msg.memAddr = mem_address
        msg.memAddrSize = addr_size

        self.send(msg)
        
    

