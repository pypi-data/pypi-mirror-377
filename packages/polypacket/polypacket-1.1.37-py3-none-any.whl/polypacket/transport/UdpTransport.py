import socket
import errno
import logging
from polypacket.transport.Transport import Transport

log = logging.getLogger(__name__)


class UdpTransport(Transport):
    def __init__(self, localPort, callback=None):
        super().__init__(callback)
        self.localPort = localPort
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = None
        self.mode = 'server'
        self.opened = False
        self.remote_address = None
        self.should_stop = False

    def __del__(self):
        self.close()
        if self.is_alive():
            self.join(timeout=1)

    def close(self):
        self.should_stop = True
        self.opened = False
        try:
            # Shutdown the socket before closing to prevent errors
            self.socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.socket.close()
        except:
            pass

    def connect(self, hostIp, hostPort):
        log.info(f"UDP targeting {hostIp}:{hostPort}")
        self.host = (hostIp, hostPort)
        self.remote_address = (hostIp, hostPort)
        self.mode = 'client'
        try:
            # For UDP, we don't actually connect, but we can set the default destination
            self.socket.connect(self.host)
            self.opened = True
            log.info("UDP Ready (client mode)")
            self.start()
        except Exception as e:
            log.error(f"Connection failed: {e}")

    def listen(self):
        try:
            self.socket.bind(('', self.localPort))
            log.info(f"UDP Listening on port: {self.socket.getsockname()[1]}")
            self.opened = True
            self.start()
        except Exception as e:
            log.error(f"Listen failed: {e}")

    def send(self, data):
        try:
            if self.mode == 'server' and self.remote_address:
                # In server mode, send to the last received address
                self.socket.sendto(data, self.remote_address)
            elif self.mode == 'client':
                # In client mode, we've already "connected" so we can just send
                self.socket.send(data)
        except Exception as e:
            self.opened = False
            log.error(f"Send failed: {e}")

    def run(self):
        self.socket.settimeout(1.0)  # Set timeout to allow periodic checks of should_stop

        while not self.should_stop and self.opened:
            try:
                if self.mode == 'server':
                    # Server mode: receive from any address
                    data, address = self.socket.recvfrom(4096)
                    if data:
                        # Store the address so we can reply to it
                        self.remote_address = address
                        if self.callback:
                            self.callback(data)
                else:
                    # Client mode: receive from connected address
                    data = self.socket.recv(4096)
                    if data:
                        if self.callback:
                            self.callback(data)
            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except IOError as e:
                if e.errno != errno.EWOULDBLOCK:
                    log.debug(f"Receive exception: {e}")
                    self.opened = False
                    break


udpConnectionHelp = """
Invalid UDP connection string. Options:

    [udp:local-port] to listen on a port
    [udp:host:remote-port] to target remote port on a host
    [udp:local-port:host:remote-port] to target remote port on host and bind to specific local port

Examples:
    udp:8080                    - Listen on port 8080
    udp:localhost:9000          - Send to localhost:9000
    udp:5000:192.168.1.10:6000  - Bind to port 5000 and send to 192.168.1.10:6000
"""


def parseUdpConnectionString(connString):
    try:
        parts = connString.split(":")
        localPort = -1
        remoteHost = None
        remotePort = -1

        if len(parts) == 2:
            # udp:local_port (server mode)
            if parts[1].isnumeric():
                localPort = int(parts[1])
            else:
                return None
        elif len(parts) == 3:
            # udp:remote_host:remote_port
            try:
                remoteHost = parts[1]
                remotePort = int(parts[2])
                localPort = 0  # Let the system choose a port
            except:
                return None
        elif len(parts) == 4:
            # udp:local_port:remote_host:remote_port
            try:
                localPort = int(parts[1])
                remoteHost = parts[2]
                remotePort = int(parts[3])
            except:
                return None
        else:
            return None

        return {'localPort': localPort, 'remoteHost': remoteHost, 'remotePort': remotePort}

    except:
        return None