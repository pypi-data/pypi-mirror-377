import asyncio
import threading
import ssl
import logging
import websocket
import websockets
from polypacket.transport.Transport import Transport

log = logging.getLogger(__name__)


class WebsocketTransport(Transport):
    def __init__(self, uri, callback=None, allow_insecure=True):
        super().__init__(callback)
        self.uri = uri
        self.allow_insecure = allow_insecure
        self.ws = None
        self.opened = False
        self.should_stop = False
        self.server = None
        self.current_websocket = None
        self.loop = None
        self.mode = 'client'
        self.port = None
        self.path = '/'  # Default path for server mode
        self.secure = False
        
    def configure_server(self, port, path='/', secure=False):
        self.mode = 'server'
        self.port = port
        self.path = path
        self.secure = secure
        
    def __del__(self):
        self.close()
        
    def close(self):
        self.should_stop = True
        if self.mode == 'client' and self.ws:
            self.ws.close()
        elif self.mode == 'server' and self.server:
            if self.loop and not self.loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(self._close_server(), self.loop)
                try:
                    future.result(timeout=1)
                except:
                    pass
            
    async def _close_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            
    def connect(self):
        try:
            if self.mode == 'client':                
                # Configure SSL options for insecure connections
                sslopt = None
                if self.uri.startswith('wss://') and self.allow_insecure:
                    sslopt = {"cert_reqs": ssl.CERT_NONE}
                    
                self.ws = websocket.WebSocketApp(
                    self.uri,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
            else:
                log.info(f"WebSocket server starting on port {self.port}")
                
            # Start the connection in a separate thread
            self.start()
            
        except Exception as e:
            log.error(f"WebSocket Exception: {e}")
            
    def send(self, data):
        try:
            if self.mode == 'client' and self.ws and self.opened:
                self.ws.send(data, opcode=websocket.ABNF.OPCODE_BINARY)
            elif self.mode == 'server' and self.current_websocket and self.opened:
                if self.loop and not self.loop.is_closed():
                    asyncio.run_coroutine_threadsafe(
                        self.current_websocket.send(data), self.loop
                    )
        except Exception as e:
            log.error(f"WebSocket Send Exception: {e}")
            self.opened = False
            
    def run(self):
        try:
            if self.mode == 'client':
                sslopt = None
                if self.uri.startswith('wss://') and self.allow_insecure:
                    sslopt = {"cert_reqs": ssl.CERT_NONE}
                    
                self.ws.run_forever(sslopt=sslopt)
            else:
                # Server mode
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_until_complete(self._start_server())
        except Exception as e:
            log.error(f"WebSocket Run Exception: {e}")
            
    async def _start_server(self):
        try:
            ssl_context = None
            if self.secure:
                ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                # For development/testing - you'd want proper certificates in production
                if self.allow_insecure:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    
            self.server = await websockets.serve(
                self._handle_client,
                "0.0.0.0",
                self.port,
                ssl=ssl_context
            )
            log.info(f"WebSocket server started on port {self.port}")
            self.opened = True
            await self.server.wait_closed()
        except Exception as e:
            log.error(f"WebSocket Server Exception: {e}")
            
    async def _handle_client(self, websocket):
        try:
            # Check if the client is connecting to the correct path
            if hasattr(websocket, 'path'):
                client_path = websocket.path
            else:
                # For newer versions, path might be in request_headers
                client_path = '/'
                if hasattr(websocket, 'request'):
                    if hasattr(websocket.request, 'path'):
                        client_path = websocket.request.path
                    elif hasattr(websocket.request, 'headers'):
                        # Try to get path from headers
                        pass

            # Only accept connections to the configured path
            if client_path != self.path:
                log.warning(f"WebSocket client rejected - requested path {client_path} but serving on {self.path}")
                await websocket.close(code=404, reason="Path not found")
                return

            log.info(f"WebSocket client connected on path {client_path}")
            self.current_websocket = websocket
            self.opened = True  # Keep server marked as opened
            async for message in websocket:
                if self.callback and not self.should_stop:
                    self.callback(message)
        except websockets.exceptions.ConnectionClosed:
            log.warning("WebSocket client disconnected")
        except Exception as e:
            log.error(f"WebSocket Client Handler Exception: {e}")
        finally:
            self.current_websocket = None
            # Don't set self.opened = False here as it affects the server status
            
    def _on_open(self, _ws):
        self.opened = True
        
    def _on_message(self, _ws, message):
        if self.callback and not self.should_stop:
            self.callback(message)
            
    def _on_error(self, _ws, error):
        log.error(f"WebSocket Error: {error}")
        self.opened = False
        
    def _on_close(self, _ws, _close_status_code, _close_msg):
        log.info("WebSocket Disconnected")
        self.opened = False


websocketConnectionHelp = """
Invalid WebSocket connection string. Options:

    [ws://host:port/path] for insecure WebSocket client connection
    [wss://host:port/path] for secure WebSocket client connection
    [ws:port] for insecure WebSocket server on specified port (serves on /)
    [ws:port/path] for insecure WebSocket server on specified port and path
    [wss:port] for secure WebSocket server on specified port (serves on /)
    [wss:port/path] for secure WebSocket server on specified port and path

Examples:
    Client connections:
        ws://localhost:8080/websocket
        wss://example.com:443/api/websocket

    Server mode:
        ws:8080              (serves on /)
        ws:8080/endpoint     (serves on /endpoint)
        wss:8443             (serves on /)
        wss:8443/api         (serves on /api)
"""


def parseWebsocketConnectionString(connString):
    try:
        if connString.startswith('ws://') or connString.startswith('wss://'):
            return {'uri': connString, 'mode': 'client'}
        elif connString.startswith('ws:') and not connString.startswith('ws://'):
            # Server mode: ws:port or ws:port/path
            server_str = connString[3:]
            path = '/'

            # Check if there's a path component
            if '/' in server_str:
                port_str, path_part = server_str.split('/', 1)
                path = '/' + path_part
            else:
                port_str = server_str

            try:
                port = int(port_str)
                return {'port': port, 'path': path, 'mode': 'server', 'secure': False}
            except ValueError:
                return None
        elif connString.startswith('wss:') and not connString.startswith('wss://'):
            # Secure server mode: wss:port or wss:port/path
            server_str = connString[4:]
            path = '/'

            # Check if there's a path component
            if '/' in server_str:
                port_str, path_part = server_str.split('/', 1)
                path = '/' + path_part
            else:
                port_str = server_str

            try:
                port = int(port_str)
                return {'port': port, 'path': path, 'mode': 'server', 'secure': True}
            except ValueError:
                return None
        else:
            return None

    except Exception:
        return None