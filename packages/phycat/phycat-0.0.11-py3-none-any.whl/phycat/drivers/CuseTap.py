#!/usr/bin/env python3
import os
import stat
import errno
from fcntl import ioctl
from threading import Thread, Lock
from collections import deque
from fuse import FUSE, Operations, FuseOSError  # Added FuseOSError here


class CUSETap(Operations):
    def __init__(self, interface):
        """
        Initialize a CUSE tap connected to a hardware interface
        
        Args:
            interface: Parent interface that bridges to remote hardware
        """
        super().__init__()
        self.interface = interface
        self.fuse_thread = None
        self.running = False
        self.lock = Lock()
        self.buffer = deque()  # Buffer for incoming data
        self.buffer_size = 0   # Track buffer size
        self.max_buffer_size = 1024 * 1024  # 1MB max buffer

    def start(self, path):
        """
        Start a CUSE device at the specified path
        
        Args:
            path: Path where the CUSE device should be created
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.running:
            return False

        try:
            abs_path = os.path.abspath(path)
            self.mount_point = abs_path
            
            print(f"Using absolute path: {abs_path}")

            # Clean up any existing file/mount first
            if os.path.exists(abs_path):
                print(f"Found existing device at {abs_path}, cleaning up...")
                # Try to unmount if it's mounted
                with open('/proc/mounts', 'r') as f:
                    if any(abs_path in line for line in f):
                        print("Unmounting existing mount...")
                        os.system(f"fusermount -u {abs_path}")
                        time.sleep(0.5)
                        os.system(f"fusermount -uz {abs_path}")
                        time.sleep(0.5)
                
                # Remove the file
                try:
                    os.chmod(abs_path, 0o666)
                    os.remove(abs_path)
                except Exception as e:
                    print(f"Failed to remove file: {e}")
                    os.system(f"sudo rm -f {abs_path}")
                
                time.sleep(0.5)  # Wait a bit after cleanup

            # Create parent directory if needed
            directory = os.path.dirname(abs_path)
            if directory:
                print(f"Creating directory: {directory}")
                os.makedirs(directory, exist_ok=True)

            # Create empty file
            with open(abs_path, 'w') as f:
                pass

            print(f"Starting FUSE thread for path: {abs_path}")
            self.fuse_thread = Thread(target=self._run_fuse, args=(abs_path,))
            self.fuse_thread.daemon = True
            self.fuse_thread.start()
            
            # Wait briefly for mount
            time.sleep(1)
            
            if os.path.exists(abs_path):
                print(f"Successfully created device at {abs_path}")
                self.running = True
                return True
            else:
                print(f"Failed to create device at {abs_path}")
                return False

        except Exception as e:
            print(f"Error starting CUSE device: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def _run_fuse(self, path):
        """Run FUSE/CUSE in a separate thread"""
        try:
            fuse_options = {
                'foreground': True,
                'dev': True,
                'raw_fi': True,
                'fsname': 'cusetap',
                'debug': True,
                'nothreads': True,
                'allow_root': True,
                'default_permissions': True,
                'subtype': 'chardev',
                'nonempty': True,  # Allow mounting over non-empty directory
            }
            
            print(f"Attempting FUSE mount at {path} with options: {fuse_options}")
            FUSE(self, path, **fuse_options)
        except Exception as e:
            print(f"FUSE error: {e}")
            import traceback
            traceback.print_exc()
            
    def cleanup(self):
        """Clean up mount point and device file"""
        try:
            if hasattr(self, 'mount_point') and self.mount_point:
                print(f"Cleaning up {self.mount_point}")
                
                # Check if it's mounted
                with open('/proc/mounts', 'r') as f:
                    if any(self.mount_point in line for line in f):
                        print("Unmounting...")
                        # Try normal unmount
                        os.system(f"fusermount -u {self.mount_point}")
                        time.sleep(0.5)
                        # Force if still mounted
                        os.system(f"fusermount -uz {self.mount_point}")
                        time.sleep(0.5)
                
                # Forcefully remove file if it still exists
                if os.path.exists(self.mount_point):
                    print(f"Removing file {self.mount_point}")
                    try:
                        os.chmod(self.mount_point, 0o666)  # Make sure we have permissions
                        os.remove(self.mount_point)
                    except Exception as e:
                        print(f"Failed to remove file: {e}")
                        # Try force remove as root if available
                        os.system(f"sudo rm -f {self.mount_point}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    def stop(self):
        """Stop the CUSE device"""
        if self.running:
            with self.lock:
                self.running = False
                if self.fuse_thread:
                    self.fuse_thread.join(timeout=1.0)
                self.buffer.clear()
                self.buffer_size = 0
                self.cleanup()

    def push_data(self, data):
        """
        Write data to the device buffer
        This is called by the interface when new data arrives from remote hardware
        
        Args:
            data: bytes to write to the device buffer
            
        Returns:
            int: Number of bytes written to buffer
        """
        if not self.running or not data:
            return 0

        with self.lock:
            # Check if buffer has space
            if self.buffer_size + len(data) > self.max_buffer_size:
                # Buffer overflow - discard oldest data
                while self.buffer and (self.buffer_size + len(data) > self.max_buffer_size):
                    old_data = self.buffer.popleft()
                    self.buffer_size -= len(old_data)

            # Add new data
            self.buffer.append(data)
            self.buffer_size += len(data)
            return len(data)

    def read(self, size, offset, fh):
        """Handle read operation from device"""
        # First check if we have buffered data
        with self.lock:
            if self.buffer:
                # Combine all buffers into one
                if len(self.buffer) > 1:
                    combined_data = b''.join(self.buffer)
                    self.buffer.clear()
                    self.buffer.append(combined_data)

                # Get data from buffer
                data = self.buffer[0]
                if len(data) <= size:
                    # Return entire buffer
                    self.buffer.popleft()
                    self.buffer_size -= len(data)
                    return data
                else:
                    # Return partial buffer
                    result = data[:size]
                    self.buffer[0] = data[size:]
                    self.buffer_size -= size
                    return result

        # If no buffered data, ask interface
        try:
            data = self.interface.on_read(size)
            return data if data else b''
        except Exception as e:
            raise OSError(errno.EIO, str(e))

    def write(self, data, offset, fh):
        """Handle write operation to device"""
        try:
            bytes_written = self.interface.on_write(data)
            return bytes_written
        except Exception as e:
            raise OSError(errno.EIO, str(e))

    def ioctl(self, cmd, arg, flags, fh):
        """Handle ioctl operation"""
        try:
            result = self.interface.on_ioctl(cmd, arg, flags)
            return result
        except Exception as e:
            raise OSError(errno.ENOTTY, str(e))

    def open(self, flags):
        """Handle device open operation"""
        try:
            self.interface.on_open(flags)
            return 0
        except Exception as e:
            raise OSError(errno.EIO, str(e))

    def release(self, flags):
        """Handle device close operation"""
        try:
            self.interface.on_close(flags)
            return 0
        except Exception as e:
            raise OSError(errno.EIO, str(e))

    def poll(self, events):
        """Handle poll operation"""
        poll_mask = 0

        # Check if we have data available to read
        with self.lock:
            if self.buffer_size > 0:
                poll_mask |= os.POLLIN

        # Ask interface if we can write
        try:
            interface_poll = self.interface.on_poll(events)
            # Combine our poll results with interface poll results
            if interface_poll & os.POLLOUT:
                poll_mask |= os.POLLOUT
            # Add any other flags from interface
            poll_mask |= (interface_poll & ~(os.POLLIN | os.POLLOUT))
        except Exception as e:
            # Default to writable if interface doesn't implement poll
            poll_mask |= os.POLLOUT

        return poll_mask
    
    # Basic filesystem operations required by FUSE
    def getattr(self, path, fh=None):
        if path == "/":
            now = time.time()
            return {
                'st_mode': (stat.S_IFCHR | 0o666),
                'st_nlink': 1,
                'st_size': 0,
                'st_ctime': now,
                'st_mtime': now,
                'st_atime': now,
                'st_uid': os.getuid(),
                'st_gid': os.getgid(),
                'st_rdev': os.makedev(180, 0)  # Use a standard char device major/minor
            }
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        return ['.', '..']

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def opendir(self, path):
        return 0

    def flush(self, path, fh):
        return 0

    def fsync(self, path, fdatasync, fh):
        return 0

    def release(self, path, fh):
        return 0

    def releasedir(self, path, fh):
        return 0

    def utimens(self, path, times=None):
        return 0

    def chmod(self, path, mode):
        return 0

    def chown(self, path, uid, gid):
        return 0

    # CUSE-specific operations
    def read(self, size, offset, fh):
        with self.lock:
            if self.buffer:
                if len(self.buffer) > 1:
                    combined_data = b''.join(self.buffer)
                    self.buffer.clear()
                    self.buffer.append(combined_data)
                data = self.buffer[0]
                if len(data) <= size:
                    self.buffer.popleft()
                    self.buffer_size -= len(data)
                    return data
                else:
                    result = data[:size]
                    self.buffer[0] = data[size:]
                    self.buffer_size -= size
                    return result
        try:
            data = self.interface.on_read(size)
            return data if data else b''
        except Exception as e:
            raise FuseOSError(errno.EIO)

    def write(self, buf, offset, fh):
        try:
            return self.interface.on_write(buf)
        except Exception as e:
            raise FuseOSError(errno.EIO)

    def truncate(self, path, length, fh=None):
        return 0
    
    def setvolname(self, name):
        """Handle SETVOLNAME (opcode 52)"""
        return 0

    def setxattr(self, path, name, value, options, position=0):
        """Handle extended attribute operations"""
        return 0

    def getxattr(self, path, name, position=0):
        """Handle get extended attribute"""
        raise FuseOSError(errno.ENODATA)

    def listxattr(self, path):
        """List extended attributes"""
        return []

    def removexattr(self, path, name):
        """Remove extended attribute"""
        raise FuseOSError(errno.ENODATA)

    def statfs(self, path):
        return {
            'f_bsize': 512,
            'f_frsize': 512,
            'f_blocks': 1,
            'f_bfree': 0,
            'f_bavail': 0,
            'f_files': 1,
            'f_ffree': 0,
            'f_favail': 0,
            'f_flag': 0,
            'f_namemax': 255
        }
    


if __name__ == "__main__":
    import time
    import signal
    import sys
    import atexit

    class ExampleInterface:
        """Example interface that echoes data and generates periodic messages"""
        def __init__(self):
            self.counter = 0
            self.thread = None
            self.running = False

        def start(self):
            """Start a background thread to generate data"""
            self.running = True
            self.thread = Thread(target=self._generate_data)
            self.thread.daemon = True
            self.thread.start()

        def stop(self):
            """Stop the background thread"""
            self.running = False
            if self.thread:
                self.thread.join()

        def _generate_data(self):
            """Generate periodic messages"""
            while self.running:
                time.sleep(1)
                if hasattr(self, 'tap'):
                    msg = f"Counter: {self.counter}\n".encode('utf-8')
                    self.tap.push_data(msg)
                    self.counter += 1

        def on_read(self, size):
            """Called when device is read from"""
            return None  # Let buffered data handle reads

        def on_write(self, data):
            """Echo written data back"""
            if hasattr(self, 'tap'):
                self.tap.push_data(b"Echo: " + data)
            return len(data)

        def on_open(self, flags):
            """Handle device open"""
            print("Device opened")
            return 0

        def on_close(self, flags):
            """Handle device close"""
            print("Device closed")
            return 0

        def on_ioctl(self, cmd, arg, flags):
            """Handle ioctl commands"""
            return 0

        def on_poll(self, events):
            """Always ready for writing"""
            return os.POLLOUT
        



  # Create interface and tap
    interface = ExampleInterface()
    tap = CUSETap(interface)
    
    # Connect interface to tap
    interface.tap = tap

    # Handle Ctrl+C and program exit
    def cleanup_handler():
        print("\nShutting down...")
        interface.stop()
        tap.stop()

    def signal_handler(sig, frame):
        cleanup_handler()
        sys.exit(0)

    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start everything up
    device_path = "virtual6"
    print(f"Starting virtual serial device at {device_path}")
    
    if tap.start(device_path):
        # Wait a moment to check if mount succeeded
        time.sleep(1)
        if not os.path.exists(device_path):
            print("Failed to mount device")
            tap.stop()
            sys.exit(1)
            
        interface.start()
        print("Device ready!")
        print(f"You can connect to it using: picocom {device_path}")
        print("Press Ctrl+C to exit")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    else:
        print("Failed to start device")
        sys.exit(1)