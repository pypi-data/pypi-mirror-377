from phycat.protocol.phycat import *
from phycat.PhycatClient import PhycatClient 



def messageHandler(msg):
    print(f"Received message: {msg}")

def main():
    client = PhycatClient()



if __name__ == "__main__":
    PhycatClient().main()