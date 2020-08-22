"""Logic for interacting with watchdog."""

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver


class _WatchdogHandler(FileSystemEventHandler):
    def __init__(self, watcher, action):
        super(_WatchdogHandler, self).__init__()
        self._watcher = watcher
        self._action = action

    def on_any_event(self, event):
        if event.is_directory:
            return
        self._action(self._watcher, getattr(event, "dest_path", event.src_path))


def _set_changed(w, _):
    w.set_changed()


class LivereloadWatchdogWatcher(object):
    """File system watchdog."""

    def __init__(self, use_polling=False):
        """Prepare a new instance.

        :param use_polling: Whether PollingObserver should be used by this instance.
        """
        super(LivereloadWatchdogWatcher, self).__init__()
        self._changed = False
        # TODO: Hack.
        # Allows the LivereloadWatchdogWatcher
        # instance to set the file which was
        # modified. Used for output purposes only.
        self._action_file = None
        if use_polling:
            self._observer = PollingObserver()
        else:
            self._observer = Observer()
        self._observer.start()

        # Compatibility with livereload's builtin watcher

        # Accessed by LiveReloadHandler's on_message method to decide if a task
        # has to be added to watch the cwd.
        self._tasks = True

        # Accessed by LiveReloadHandler's watch_task method. When set to a
        # boolean false value, everything is reloaded in the browser ('*').
        self.filepath = None

        # Accessed by Server's serve method to set reload time to 0 in
        # LiveReloadHandler's poll_tasks method.
        self._changes = []

    def set_changed(self):
        """Note that changes were made."""
        self._changed = True

    def examine(self):
        """Would be called by LiveReloadHandler's poll_tasks method.

        Returns whether the waiters (browsers) are reloaded.
        """
        if self._changes:
            return self._changes.pop()

        action_file = None
        if self._changed:
            self._changed = False
            action_file = self._action_file or True  # TODO: Hack (see above)
        return action_file, None

    def watch(self, path, action, *args, **kwargs):
        """Prepare event handlers to watch for changes.

        Called by the Server instance when a new watch task is requested.
        """
        if action is None:
            action = _set_changed
        event_handler = _WatchdogHandler(self, action)
        self._observer.schedule(event_handler, path=path, recursive=True)

    def start(self, callback):
        """Start the watcher running, calling callback when changes are observed.

        If this returns False, regular polling will be used.
        """
        return False
