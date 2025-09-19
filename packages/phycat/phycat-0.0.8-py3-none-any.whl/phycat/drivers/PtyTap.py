
import pty 
import threading
import os


class PTYTap:
    def __init__(self, interface):
        self.interface = interface
        self.master, self.slave = pty.openpty()
        self.slave_name = os.ttyname(self.slave)
        self.symlink_created = False
        self.custom_path = None
        self.running = False
        self.read_thread = None

    def start(self, custom_path=None):
        """Start the PTY tap with optional custom path"""
        self.custom_path = custom_path
        if custom_path:
            try:
                if os.path.exists(custom_path):
                    if os.path.islink(custom_path) or os.path.isfile(custom_path):
                        os.remove(custom_path)
                    else:
                        raise Exception(f"Path exists and is not a symlink or file: {custom_path}")
                
                os.makedirs(os.path.dirname(os.path.abspath(custom_path)), exist_ok=True)
                os.symlink(self.slave_name, custom_path)
                self.symlink_created = True
            except Exception as e:
                print(f"Error creating symlink: {e}")
                return False

        self.running = True
        self.read_thread = threading.Thread(target=self._read_loop)
        self.read_thread.daemon = True
        self.read_thread.start()
        
        device_path = self.custom_path or self.slave_name
        print(f"PTY tap created at: {device_path}")
        return True

    def write(self, data):
        """Write data received from UART to the PTY"""
        if self.running:
            try:
                os.write(self.master, data if isinstance(data, bytes) else data.encode())
            except OSError as e:
                print(f"Error writing to PTY: {e}")

    def _read_loop(self):
        """Thread that reads from PTY and sends to UART"""
        while self.running:
            try:
                data = os.read(self.master, 1024)
                if data:
                    self.interface.write(data)
            except OSError:
                # Handle disconnection or other errors
                continue

    def stop(self):
        """Stop the PTY tap and clean up"""
        self.running = False
        if self.read_thread:
            self.read_thread.join()
        
        if self.symlink_created and self.custom_path:
            try:
                os.remove(self.custom_path)
            except Exception as e:
                print(f"Error removing symlink: {e}")
        
        os.close(self.master)
        os.close(self.slave)

