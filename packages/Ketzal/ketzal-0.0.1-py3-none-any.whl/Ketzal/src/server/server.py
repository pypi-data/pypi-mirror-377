from Ketzal.src.config.config import Config
from .RequestHandler import RequestHandler
from .RouteLoader import RouteLoader
from .FileWatcher import FileWatcherManager
from .SocketManager import SocketManager


class Server:
    """
    Main HTTP server – coordinates core components such as sockets, routes,
    request handling, and hot-reloading of source code.

    Attributes:
        config (Config): Holds server configuration (host, port, etc.).
        auto_reload (bool): Whether to automatically reload routes on file changes.
        socket_manager (SocketManager): Manages the server socket.
        request_handler (RequestHandler): Handles client HTTP requests.
        route_loader (RouteLoader): Loads and reloads routes.
        file_watcher (FileWatcherManager | None): Watches source files for changes.
    """

    def __init__(self, auto_reload=True):
        """
        Initialize the server and prepare core components.
        
        Args:
            auto_reload (bool): Enables file watching and auto-reload if True.
        """
        self.config = Config()
        self.auto_reload = auto_reload

        self.socket_manager = SocketManager(self.config.host, self.config.port)
        self.request_handler = RequestHandler()
        self.route_loader = RouteLoader()
        self.file_watcher = None

        self._initialize_server()

    def _initialize_server(self):
        """
        Loads routes and sets up the server socket.
        If auto_reload is enabled, also starts the file watcher.
        """
        self.route_loader.load_routes(self.config)
        if not self.socket_manager.setup_socket():
            raise Exception("Failed to setup server socket")

        if self.auto_reload:
            self.file_watcher = FileWatcherManager(self._on_file_change)
            self.file_watcher.start_file_watcher()

    def _on_file_change(self):
        """
        Callback executed when a file change is detected by the file watcher.
        Reloads the routes dynamically.
        """
        self.route_loader.reload_routes(self.config)

    def start(self):
        """
        Starts the main server loop. Waits for incoming client connections,
        processes requests, and handles errors gracefully.
        Supports clean shutdown with Ctrl+C (KeyboardInterrupt).
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
                        print(f"📩 {address[0]} requested: {response_info['request_line']}, {self.socket_manager.get_address()}")

                except Exception as e:
                    # Catch per-client errors, keep server running
                    print(f"❌ Client request error: {e}")

        except KeyboardInterrupt:
            # Gracefully handle Ctrl+C shutdown
            self.shutdown()

    def shutdown(self):
        """
        Gracefully shuts down the server:
        - Stops the file watcher if running.
        - Closes the server socket.
        """
        if self.file_watcher:
            self.file_watcher.stop_file_watcher()
        self.socket_manager.close_socket()
        print("👋 Server shutdown complete")

    def restart(self):
        """
        Restarts the server by:
        - Stopping the file watcher.
        - Closing the current socket.
        - Re-initializing routes and sockets.
        """
        if self.file_watcher:
            self.file_watcher.stop_file_watcher()
        self.socket_manager.close_socket()
        self._initialize_server()
