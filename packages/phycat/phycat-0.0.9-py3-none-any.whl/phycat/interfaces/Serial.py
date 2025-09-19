import serial
from phycat.interfaces.Interface import PhycatInterface
from phycat.protocol import *
import threading


class SerialRunner(threading.Thread):
    def __init__(self, parent, port, baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0.1):
        threading.Thread.__init__(self)
        self.interface = parent

        try:

            self.serialPort = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout
            )
            self.opened = True
            print(f"Opened {port} at {baudrate} baud")
        except serial.SerialException as e:
            print(e)
            print(f"Failed to open {port} at {baudrate} baud")

    def __del__(self):
        self.close()
        self.join()

    def close(self):
        if self.opened:
            self.serialPort.close()

    def send(self, data):
        if self.opened:
            self.serialPort.write(data)

    def run(self):
        if self.opened:
            while True:
                if self.serialPort.inWaiting() > 0:
                    data = self.serialPort.read()
                    self.handleIncomingData(data)


class Serial(PhycatInterface):
    def __init__(self, session, handle, parameters = {}):
        super().__init__(session, handle)
        self.runner = None
        self.device = parameters.get("device", None)


    def send(self, msg):
        self.serial.write(msg)
        pass

    def bringUp(self, config: UartConfig):
        
        baud  = config.baud
        parity = config.parity
        stopbits = config.stopbits
        bytesize = config.databits

        self.runner = SerialRunner(self, self.device, baud, parity, stopbits, bytesize)

    def getCapabilities(self):
        
        caps = UartCapabilities()
        caps.max_baud_rate = 115200

        return caps


    def shutdown(self):
        self.runner.close()
        self.runner.join()
        self.runner = None

    def handleMessage(self, msg):

        if isinstance(msg, UartData):
            self.runner.send(msg.data)

        elif isinstance(msg, UartConfig):
            self.bringUp(msg)

        # elif isinstance(msg,):
        #     self.send


