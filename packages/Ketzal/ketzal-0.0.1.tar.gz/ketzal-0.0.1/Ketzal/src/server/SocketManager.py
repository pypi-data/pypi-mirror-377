import socket

class SocketManager:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_listening = False

    def setup_socket(self):
        """
        Setup the server socket and start listening for incoming connections.
        Returns True if the setup was successful, False otherwise.
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            # Add timeout so Ctrl+C works
            self.server_socket.settimeout(1.0)  

            self.is_listening = True
            return True
        except Exception as e:
            print(f"❌ Error setting up socket: {e}")
            return False

    def accept_connection(self):
        """
        Accepts an incoming connection and returns the client socket and address.

        Returns (client_socket, address) if a connection is accepted, (None, None) otherwise.
        """
        if not self.is_listening or not self.server_socket:
            return None, None
            
        try:
            return self.server_socket.accept()
        except socket.timeout:
            return None, None
        except Exception as e:
            print(f"❌ Error accepting connection: {e}")
            return None, None

    def close_socket(self):
       
        if self.server_socket:
            try:
                self.server_socket.close()
                self.is_listening = False
                return True
            except Exception as e:
                print(f"⚠️ Error closing socket: {e}")
                return False
        return True

    def get_address(self):
        """Obtiene la dirección del servidor"""
        return f"http://{self.host}:{self.port}"

    def is_socket_active(self):
        """Verifica si el socket está activo"""
        return self.is_listening and self.server_socket is not None
