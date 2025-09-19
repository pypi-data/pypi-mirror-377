from phycat.drivers import PhycatInterfaceDriver
from phycat.protocol.phycatService import *
from cliify import commandParser, command
from phycat.drivers.PtyTap import PTYTap
from phycat.helpers.format_helper import hexdump
from polypacket.polyservice import PolyPacket 
from termcolor import colored
try:
    from phycat.drivers.CuseTap import CUSETap
    FUSE_AVAILABLE = True
except ImportError:
    FUSE_AVAILABLE = False

class UartInterface(PhycatInterfaceDriver):
    def __init__(self, session, handle, capabilities=None):
        super().__init__(session, handle)
        self.capabilities = capabilities
        self.cfg = None
        self.pty = None
        self.cuse = None
        self.format = None
    
    @command(completions={'parity': ['NONE', 'ODD', 'EVEN']})
    def config(self, baudrate=9600, stopBits=1, parity: str = 'NONE', dataBits=8):
        cfg = UartConfig()
        cfg.baudrate = baudrate
        cfg.stopBits = stopBits
        cfg.parity = 0
        cfg.dataBits = dataBits


        shorthand = f"{baudrate}:{dataBits}{ parity[0].upper()}{stopBits}"

        if parity.lower() == 'odd':
            cfg.parity = 1
        elif parity.lower() == 'even':
            cfg.parity = 2

        print(colored(f"[{self.name}] Config: {shorthand}", 'yellow'))
        self.configure(cfg)

    def configure(self, cfg):
        self.cfg = cfg
        self.send(cfg)

    @command(completions={'format': ['ASCII', 'BINARY', 'HEX', 'HEXDUMP']})
    def setFormat(self, format: str):
        """Set the UART format"""
        if format.lower() not in ['ascii', 'binary', 'hex', 'hexdump']:
            print(f"Unknown format: {format}")
            return False
        
        self.format = format.lower()
        print(colored(f"[{self.name}] Setting format to {self.format}", 'yellow'))

    @command(completions={'file': ['$file']})
    def write(self, data: bytes = b'', file: str = None):


        if file:
            try:
                with open(file, 'rb') as f:
                    data = f.read()
                    
                print(colored(f"[{self.name}] --> {file}", 'blue'))
                
                # print the first 16 bytes of the file
            except Exception as e:
                print(colored(f"Error reading file {file}: {e}", 'red'))
                return False
        elif len(data) > 0:

            display_data = ""
            if self.format == 'ascii': # 'Hello World'
                display_data = data.decode('ascii', errors='replace')
            elif self.format == 'binary': #0b0001010 
                display_data = ' '.join(f'{byte:08b}' for byte in data)
            else: # 0x01 0x02 0x03
                display_data = ' '.join(f'0x{byte:02x}' for byte in data)

            print(colored(f"[{self.name}] --> {display_data}", 'blue'))

        while len(data) > 0:
            chunk = data[:64]
            msg = UartData()
            msg.handle = self.handle
            msg.data = chunk
            data = data[64:]

            self.send(msg)

    @command(completions={'name': ['$file']})
    def tap(self, name):
        """Open a PTY tap at the specified path"""
        if self.pty:
            print("PTY tap already exists. Close it first.")
            return False
        
        self.pty = PTYTap(self)
        if not self.pty.start(name):
            self.pty = None
            return False
        return True
    
    @command(completions={'name': ['$file']})
    def tap2(self, name):
        """Open a CUSE tap at the specified path"""
        if not FUSE_AVAILABLE:
            print("CUSE/FUSE is not available. Please install the 'fusepy' library.")
            return False


        if self.cuse:
            self.cuse.close()
        
        self.cuse = CUSETap(self)
        if not self.cuse.start(name):
            self.cuse = None
            return False
        return True

    def close_tap(self):
        """Close the PTY tap if it exists"""
        if self.pty:
            self.pty.stop()
            self.pty = None

    def handle_data(self, uartData: UartData):
        print(f"{self.name} <-- {uartData.data}")
        
        if self.pty:
            self.pty.write(uartData.data)

        if self.cuse:
            self.cuse.write(uartData.data)
    
    def handleMessage(self, msg: PolyPacket):
        data = msg.toBasePacket().data
        display_data = ""
        if self.format == 'ascii':
            #convert list of bytes to ascii string
            if isinstance(data, list):
                data = bytes(data)
            display_data = colored(f"[{self.name}] <-- " + data.decode('ascii', errors='replace'), 'green')
        elif self.format == 'binary':
            display_data = colored(f"[{self.name}] <-- " + ' '.join(f'{byte:08b}' for byte in data), 'green')
        elif self.format == 'hexdump':
            display_data = colored(f"[{self.name}] <--[ ... ]",'green')
            display_data += '\n\n' + hexdump(data) + "\n"
        else :
            display_data = colored(f"[{self.name}] <-- " + ' '.join(f'0x{byte:02x}' for byte in data), 'green')
            
        print(display_data)

    def on_cuse_ioctl(self, cmd,arg,flags):
        print(f"IOCTL {cmd} {arg} {flags} {data}")
        return 0
    
    def on_cuse_write(self, data):
        print(f"WRITE {data}")
        return len(data)
    
    def on_cuse_read(self, size):
        print(f"READ {size}")
        return b''
    

