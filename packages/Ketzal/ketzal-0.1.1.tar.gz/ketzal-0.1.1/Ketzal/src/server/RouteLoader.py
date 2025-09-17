import os
import sys
import time
import importlib.util
from Ketzal.src.routing.Router import Router

class RouteLoader:
    """Handles loading and reloading of application routes."""

    def __init__(self):
        # Timestamp of the last time routes were successfully loaded
        self.routes_loaded_time = None

    def load_routes(self, config=None):
        """
        Load routes from the default routes/web.py file.
        
        Args:
            config (Config, optional): Optional configuration object.
        """
        web_path = os.path.join(os.getcwd(), "routes", "web.py")
        if not os.path.exists(web_path):
            # Only show message if missing
            print("⚠️ routes/web.py not found")
            return

        try:
            # Clear routes before loading
            if hasattr(Router, 'clear_routes'):
                Router.clear_routes()
            elif hasattr(Router, 'routes'):
                Router.routes.clear()

            spec = importlib.util.spec_from_file_location("web_routes", web_path)
            web_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(web_module)
            self.routes_loaded_time = time.time()
        except Exception as e:
            print(f"❌ Error loading routes: {e}")

    def reload_routes(self, config=None):
        """
        Reload routes when file changes are detected.
        
        Args:
            config (Config, optional): Optional configuration object.
        """
        print("🔄 Reloading routes...")
        try:
            # Clear cached modules and reload routes
            self._clear_module_cache()
            self.load_routes(config)
            print("✅ Routes reloaded successfully")
        except Exception as e:
            print(f"❌ Error reloading routes: {e}")

    def _clear_route_cache(self):
        """Clear in-memory route definitions in Router."""
        try:
            if hasattr(Router, 'clear_routes'):
                Router.clear_routes()
            elif hasattr(Router, 'routes'):
                Router.routes.clear()
        except Exception as e:
            print(f"⚠️ Warning clearing route cache: {e}")

    def _clear_module_cache(self):
        """Remove route- and controller-related modules from Python cache."""
        modules_to_remove = []

        for module_name in sys.modules:
            if ('routes' in module_name or
                'controllers' in module_name or
                'web_routes' in module_name):
                modules_to_remove.append(module_name)

        for module_name in modules_to_remove:
            try:
                del sys.modules[module_name]
            except KeyError:
                pass

    def _get_web_routes_path(self):
        """Return the filesystem path for routes/web.py."""
        return os.path.join(os.getcwd(), "routes", "web.py")

    def _import_web_routes(self, web_path):
        """
        Import the web routes module dynamically.

        Args:
            web_path (str): Full path to the routes/web.py file.
        
        Raises:
            Exception: If import fails, prints detailed traceback.
        """
        try:
            spec = importlib.util.spec_from_file_location("web_routes", web_path)
            web_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(web_module)
        except Exception as e:
            print(f"❌ Detailed import error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
