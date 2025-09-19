from phycat.interfaces import PhycatInterface
from phycat.protocol.phycatService import *

class Gpio(PhycatInterface):
    def __init__(self, session, handle, capabilities = None):
        super().__init__(session, handle)

        self.capabilities = capabilities
        self.config = None

    def configure(self, config):
        self.config = config

        self.send( config )

    def write(self, address, data):
        msg = UartData()
        msg.handle = self.handle
        msg.data = data

        self.send(msg)