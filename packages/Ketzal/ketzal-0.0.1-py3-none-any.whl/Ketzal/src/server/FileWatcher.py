import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileWatcher(FileSystemEventHandler):
    """
    Custom file system event handler that triggers a callback when
    Python files (*.py) are modified.

    Attributes:
        callback (function): Function to execute when a file changes.
        last_modified (dict): Keeps track of last modification times to debounce events.
    """

    def __init__(self, callback):
        self.callback = callback
        self.last_modified = {}

    def on_modified(self, event):
        """
        Triggered when a file or directory is modified.
        Only reacts to .py files and debounces rapid successive changes.
        """
        if event.is_directory:
            return

        if not event.src_path.endswith('.py'):
            return

        current_time = time.time()
        if event.src_path in self.last_modified:
            # Debounce: ignore duplicate events within 1 second
            if current_time - self.last_modified[event.src_path] < 1:
                return

        self.last_modified[event.src_path] = current_time

        print(f"🔄 File changed: {event.src_path}")
        self.callback()


class FileWatcherManager:
    """
    Manages the file system observer for monitoring source code changes.

    Attributes:
        observer (Observer): The watchdog observer instance.
        reload_callback (function): Function executed when changes are detected.
        is_active (bool): Indicates if the watcher is currently active.
    """

    def __init__(self, reload_callback):
        self.observer = None
        self.reload_callback = reload_callback
        self.is_active = False

    def start_file_watcher(self):
        """
        Start watching source code directories for changes.
        Observes 'routes', 'controllers', and 'Ketzal/src'.
        """
        try:
            self.observer = Observer()
            event_handler = FileWatcher(self.reload_callback)

            # Watch the routes directory
            self._watch_directory("routes", event_handler)

            # Watch the controllers directory (if it exists)
            self._watch_directory("controllers", event_handler)

            # Watch the Ketzal/src directory
            ketzal_src = os.path.join(os.getcwd(), "Ketzal", "src")
            if os.path.exists(ketzal_src):
                self.observer.schedule(event_handler, ketzal_src, recursive=True)

            self.observer.start()
            self.is_active = True

        except Exception as e:
            print(f"⚠️ Could not start file watcher: {e}")
            print("💡 Install watchdog: pip install watchdog")
            return False

        return True

    def _watch_directory(self, dir_name, event_handler):
        """
        Internal helper to watch a specific directory if it exists.

        Args:
            dir_name (str): Directory name relative to the current working directory.
            event_handler (FileWatcher): Handler that reacts to file modifications.
        """
        dir_path = os.path.join(os.getcwd(), dir_name)
        if os.path.exists(dir_path):
            self.observer.schedule(event_handler, dir_path, recursive=True)
            print(f"👀 Watching {dir_name}: {dir_path}")

    def stop_file_watcher(self):
        """
        Stops the file observer and releases resources.

        Returns:
            bool: True if successfully stopped, False otherwise.
        """
        if self.observer and self.is_active:
            self.observer.stop()
            self.observer.join()
            self.is_active = False
            print("✅ File watcher stopped")
            return True
        return False

    def is_watching(self):
        """
        Checks if the file watcher is active.

        Returns:
            bool: True if active, False otherwise.
        """
        return self.is_active and self.observer is not None
