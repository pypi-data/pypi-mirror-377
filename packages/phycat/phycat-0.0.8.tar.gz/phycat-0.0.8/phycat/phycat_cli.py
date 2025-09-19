import os
import argparse
import importlib.metadata
import signal
import sys
from phycat.PhycatClient import PhycatClient
from phycat.PhycatServer import PhycatServer
from cliify.ui.prompt_toolkit import SplitConsole
from phycat.helpers.log_helper import configure_logging


args = None
parser = None

version = importlib.metadata.version("phycat")



banner_text =f"Phycat v{version}"

# Initialize the argument parser
def init_args():
    global parser
    parser = argparse.ArgumentParser("Tool to interact with replicant message broker")
    parser.add_argument('-c', '--connect', type=str, help='Stack Base Address', default=None)
    parser.add_argument('-s', '--server', type=str, help='Server Config', default=None)
    parser.add_argument('-l','--log-level', type=str, help='Log Level', default="info")
    parser.add_argument('-i','--interface-dir', action='append', help='Additional interface directories', default=[])


def main():
    global args
    global parser

    init_args()
    args = parser.parse_args()
    configure_logging(print,args.log_level)

    if args.server is not None:
        server = PhycatServer(server_config = args.server, interface_dirs = args.interface_dir)
        
        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            print("\nShutting down server...")
            server.close()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the server
        server.start(args.connect)
        
        # Keep the server running
        try:
            signal.pause()  # Wait for signal (works on Unix-like systems)
        except AttributeError:
            # On Windows, signal.pause() doesn't exist, so use a loop
            import time
            while True:
                time.sleep(1)
    else:
        home_path = os.path.expanduser('~')
        client = PhycatClient()
        app = SplitConsole(client, banner_text, os.path.join(home_path, '.phycat-history'), exitCallback=client.close, logLevel=args.log_level)

        if args.connect:
            client.connect(args.connect)

        app.start()


if __name__ == '__main__':
   main()