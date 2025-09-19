#!/usr/bin/env python

import argparse
# get package directory
import os
import sys
import importlib.resources
import yaml
from polypacket.protocol import Protocol , buildProtocol
from polypacket.polyservice import PolyPacket, PolyService
from phycat.protocol.phycatService import handleType
import re
import jinja2


args = None
parser = None
protocol = None
service = None

ports = []
capabilities = []

typeLabels = {
    'i2c': handleType.I2C,
    'spi': handleType.SPI,
    'uart': handleType.UART,
    'can': handleType.CAN,
    'gpio': handleType.GPIO,
    'tim': handleType.TIM,
    'display': handleType.DISPLAY
}



class LabeledPort:
    def __init__(self, idx: int, label: str):
        self.handle = handleType.PORT << 16 | idx
        self.label = label


def get_pin_handle(name:str):

    for port in ports:
        if name.startswith(port.label):
            pin = int(name[len(port.label):])
            return port.handle << 16 | pin
    
    raise ValueError(f"Invalid pin name {name}")
        
        

class RenderedCapabilties:
    def __init__(self, name, descriptor: dict):
        self.name = name.lower()
        #copy the descriptor
        self.descriptor = descriptor
        self.handle = None
        self.packed :bytes = None
        self.type = None
        self.packetType = None


        for key, value in typeLabels.items():
            if self.name.startswith(key):
                self.type = self.name[:len(key)]
                idx = int(self.name[len(key):])

                self.handle = value << 16 | idx
                break

        if self.handle is None:
            raise ValueError(f"Invalid capability name {self.name}")
        
        self.packetType = self.name.capitalize() + "Capabilities"

        packet = service.newPacket(self.packetType)
        
        for key, value in self.descriptor.items():
            if key.endswith('_pin'):
                val = get_pin_handle(value)
                packet.setField(key, val)
            if key.lower().endswith('_flags') and isinstance(value, list):
                flags = ' | '.join(value)
                packet.setField(key, flags)
            else:
                packet.setField(key, value)

        self.packed = packet.pack()



        



def parse_file(file:str):
    global capabilities
    global ports
    with open(file, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if 'ports' not in data:
        print("No ports in the file")
        return None
    
    for i in range(len(data['ports'])):
        newPort = LabeledPort(i, data['ports'][i])

    for name, cap in data['capabilities'].items():
        newCap = RenderedCapabilties(name, cap)

        capabilities.append(newCap)


def render_template():
    global capabilities
    global protocol
    global service
    global args

    if args.output is None:
        print("No output file specified")
        return
    
    package_root = importlib.resources.files("phycat") 
    template_header_path = os.path.join(package_root, "templates", "capabilities.h.j2")
    template_source_path = os.path.join(package_root, "templates", "capabilities.c.j2")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="/"))
    template_header = env.get_template(template_header_path)
    header_out = template_header.render(capabilities=capabilities, protocol=protocol, service=service)

    template_source = env.get_template(template_source_path)
    source_out = template_source.render(capabilities=capabilities, protocol=protocol, service=service)



    env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="/"))

    header_out_path = os.path.join(os.getcwd(), args.output, "capabilities.h")
    source_out_path = os.path.join(os.getcwd(), args.output, "capabilities.c")
    with open(header_out_path, 'w') as f:
        f.write(header_out)

    with open(source_out_path, 'w') as f:
        f.write(source_out)


    



# Initialize the argument parser
def init_args():
    global parser
    parser = argparse.ArgumentParser("Tool to generate phcyat code")
    #positional arg for input
    parser.add_argument('input', type=str, help='Input file')
    parser.add_argument('-o', '--output', type=str, help='Output file', default=None)


def main():
    global args
    global protocol
    global parser
    global service
    init_args()
    args = parser.parse_args()
    print(args)
    

    #parse protocol 
    phycat_root = importlib.resources.files("phycat")
    poly_file = os.path.join(phycat_root, "protocol","poly", "phycat.yaml")
    protocol = buildProtocol(poly_file)
    service = PolyService(protocol)


    #get the input file
    if not os.path.exists(args.input):
        print(f"Input file {args.input} does not exist")
        sys.exit(1)

    


if __name__ == '__main__':
    main()

