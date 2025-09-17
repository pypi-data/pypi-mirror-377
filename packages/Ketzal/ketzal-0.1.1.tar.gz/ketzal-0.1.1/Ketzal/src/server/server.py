import os
from Ketzal.src.config.config import Config
from .RequestHandler import RequestHandler
from .RouteLoader import RouteLoader
from .FileWatcher import FileWatcherManager
from .SocketManager import SocketManager

from ..util.structure import structure

class Server:
    """
    Main HTTP server – coordinates sockets, routes, request handling,
    and hot-reloading of source code.
    """
    def __init__(self, auto_reload=True):
        """
        Initialize the server and prepare core components.
        """

        self.config = Config()
        self.auto_reload = auto_reload
        self.REQUIRED_STRUCTURE = structure
        self.socket_manager = SocketManager(self.config.host, self.config.port)
        self.request_handler = RequestHandler()
        self.route_loader = RouteLoader()
        self.file_watcher = None

        # Validate project structure
        if not self._validate_structure():
            raise Exception("❌ Project structure is invalid. Run `ketzal new <name>` first.")

        self._initialize_server()

    def _validate_structure(self):
        """
        Verifies that the required project structure exists.
        """
        base_path = os.getcwd()
        missing = []

        for path in self.REQUIRED_STRUCTURE:
            full_path = os.path.join(base_path, path)
            if not os.path.exists(full_path):
                missing.append(path)

        if missing:
            print("⚠️ Missing required project directories:")
            for m in missing:
                print(f"   - {m}")
            return False

        return True

    def _initialize_server(self):
        """
        Loads routes and sets up the server socket.
        """
        self.route_loader.load_routes(self.config)
        if not self.socket_manager.setup_socket():
            raise Exception("❌ Failed to setup server socket")

        if self.auto_reload:
            self.file_watcher = FileWatcherManager(self._on_file_change)
            self.file_watcher.start_file_watcher()

    def _on_file_change(self):
        """Reload routes when files change"""
        self.route_loader.reload_routes(self.config)

    def start(self):
        """
        Start main loop.
        """
        print(f"🚀 Server started {self.socket_manager.get_address()}")
        try:
            while True:
                try:
                    client_socket, address = self.socket_manager.accept_connection()
                    if client_socket is None:
                        continue

                    response_info = self.request_handler.handle_client_request(client_socket)
                    if response_info and response_info.get("request_line"):
                        if address is not None:
                            print(f"📩 {address[0]} requested: {response_info['request_line']} -> {self.socket_manager.get_address()}")
                        else:
                            print(f"📩 Unknown address requested: {response_info['request_line']} -> {self.socket_manager.get_address()}")

                except Exception as e:
                    print(f"❌ Client request error: {e}")

        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Shutdown gracefully"""
        if self.file_watcher:
            self.file_watcher.stop_file_watcher()
        self.socket_manager.close_socket()
        print("👋 Server shutdown complete")

    def restart(self):
        """Restart server"""
        if self.file_watcher:
            self.file_watcher.stop_file_watcher()
        self.socket_manager.close_socket()
        self._initialize_server()
