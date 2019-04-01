"""
Automatic builder for Sphinx based documentation sets.

MIT License. See LICENSE for more details.
Copyright (c) 2013, Jonathan Stoppani, Fork by Carrot & Company
"""

import argparse
import fnmatch
import os
import re
import subprocess
import sys
import port_for
from threading import Thread, Lock
from collections import deque
import time

try:
    import pty
except ImportError:
    pty = None

from livereload import Server

from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

__version__ = '0.7.1'
__url__ = 'https://github.com/carrotandcompany/sphinx-autobuild'

DEFAULT_IGNORE_REGEX = [
    r'__pycache__/.*\.py',
    r'.*\.pyc',
    r'.*\.kate-swp',
]

DEFAULT_EVENT_DELAY_TIME = 5


class EventActionData(object):
    def __init__(self):
        self.lock = Lock()
        self.queue = deque()


class EventActionThread(Thread):
    """
    This Thread runs an endless loop which checks every defined interval time
    if the the FileSystemEvent Queue has entries.
    If the queue has entries it empties the queue and invokes an action

    """

    def __init__(self, event_action_data, action, watcher,
                 check_interval=DEFAULT_EVENT_DELAY_TIME):
        super().__init__()
        self.action = action
        self.event_action_data = event_action_data
        self.watcher = watcher
        self.check_interval = check_interval
        self._kill_received = False

    def run(self):
        print('EventActionThread is running.')
        while not self._kill_received:
            with self.event_action_data.lock:
                if len(self.event_action_data.queue) > 0:
                    print('{} files changed. Building...'.format(
                        len(self.event_action_data.queue)))
                    # clear queue and remember the last_event
                    last_event = self.event_action_data.queue.popleft()
                    self.event_action_data.queue.clear()
                    # call the action
                    self.action(self.watcher,
                                getattr(last_event, 'dest_path',
                                        last_event.src_path))
            time.sleep(self.check_interval)

    def kill(self):
        self._kill_received = True


class _WatchdogHandler(FileSystemEventHandler):

    def __init__(self, watcher, action, event_action_data):
        super(_WatchdogHandler, self).__init__()
        self._watcher = watcher
        self._action = action
        self.event_action_data = event_action_data

    def on_any_event(self, event):
        if event.is_directory:
            return
        with self.event_action_data.lock:
            self.event_action_data.queue.append(event)


def _set_changed(w, _):
    w.set_changed()


class LivereloadWatchdogWatcher(object):
    """
    File system watch dog.
    """

    def __init__(self, event_queue, use_polling=False):
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
            self._observer = Observer(timeout=1000)
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

        self.event_queue = event_queue

    def set_changed(self):
        self._changed = True

    def examine(self):
        """
        Called by LiveReloadHandler's poll_tasks method.

        If a boolean true value is returned, then the waiters (browsers) are
        reloaded.
        """
        if self._changes:
            return self._changes.pop()

        action_file = None
        if self._changed:
            self._changed = False
            action_file = self._action_file or True  # TODO: Hack (see above)
        return action_file, None

    def watch(self, path, action, *args, **kwargs):
        """
        Called by the Server instance when a new watch task is requested.
        """
        if action is None:
            action = _set_changed
        event_handler = _WatchdogHandler(self, action, self.event_queue)
        self._observer.schedule(event_handler, path=path, recursive=True)

    def start(self, callback):
        """
        Start the watcher running, calling callback when changes are
        observed.

        If this returns False, regular polling will be used.
        """
        return False


class SphinxBuilder(object):
    """
    Helper class to run sphinx-build command.
    """

    def __init__(self, outdir, args, ignored=None, regex_ignored=None):
        self._outdir = outdir
        self._args = args
        self._ignored = ignored or []
        self._ignored.append(outdir)
        self._regex_ignored = [re.compile(r) for r in regex_ignored or []]

    def is_ignored(self, src_path):
        path = self.get_relative_path(src_path)
        for i in self._ignored:
            if fnmatch.fnmatch(path, i):
                return True
            if src_path.startswith(i + os.sep):
                return True

        for r in self._regex_ignored:
            if r.search(src_path):
                return True

    def __call__(self, watcher, src_path):

        path = self.get_relative_path(src_path)

        if self.is_ignored(src_path):
            return

        watcher._action_file = path  # TODO: Hack (see above)

        self.build(path)

    def build(self, path=None):
        if path:
            pre = '+--------- {0} changed '.format(path)
        else:
            pre = '+--------- manually triggered build '
        sys.stdout.write('\n')
        sys.stdout.write(pre)
        sys.stdout.write('-' * (81 - len(pre)))
        sys.stdout.write('\n')
        args = ['sphinx-build'] + self._args
        if pty:
            master, slave = pty.openpty()
            stdout = os.fdopen(master)
            subprocess.Popen(args, stdout=slave)
            os.close(slave)
        else:
            stdout = subprocess.Popen(args,
                                      stdout=subprocess.PIPE,
                                      universal_newlines=True).stdout
        try:
            while 1:
                line = stdout.readline()
                if not line:
                    break
                sys.stdout.write('| ')
                sys.stdout.write(line.rstrip())
                sys.stdout.write('\n')
        except IOError:
            pass
        finally:
            if not pty:
                stdout.close()
        sys.stdout.write('+')
        sys.stdout.write('-' * 80)
        sys.stdout.write('\n\n')

    def get_relative_path(self, path):
        return os.path.relpath(path)


SPHINX_BUILD_OPTIONS = (
    ('b', 'builder'),
    ('a', None),
    ('E', None),
    ('d', 'path'),
    ('j', 'N'),

    ('c', 'path'),
    ('C', None),
    ('D', 'setting=value'),
    ('t', 'tag'),
    ('A', 'name=value'),
    ('n', None),

    ('v', None),
    ('q', None),
    ('Q', None),
    ('w', 'file'),
    ('W', None),
    ('T', None),
    ('N', None),
    ('P', None),
)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8000)
    parser.add_argument('-H', '--host', type=str, default='127.0.0.1')
    parser.add_argument('-ed', '--event-delay', type=int,
                        default=DEFAULT_EVENT_DELAY_TIME)
    parser.add_argument('-r', '--re-ignore', action='append', default=[])
    parser.add_argument('-i', '--ignore', action='append', default=[])
    parser.add_argument('--poll', dest='use_polling',
                        action='store_true', default=False)
    parser.add_argument('--no-initial', dest='initial_build',
                        action='store_false', default=True)
    parser.add_argument('-B', '--open-browser', dest='openbrowser',
                        action='store_true', default=False)
    parser.add_argument('-s', '--delay', dest='delay', type=int, default=5)
    parser.add_argument('-z', '--watch', action='append', metavar='DIR',
                        default=[],
                        help=('Specify additional directories to watch. May be'
                              ' used multiple times.'),
                        dest='additional_watched_dirs')
    parser.add_argument('--version', action='version',
                        version='sphinx-autobuild {}'.format(__version__))

    for opt, meta in SPHINX_BUILD_OPTIONS:
        if meta is None:
            parser.add_argument('-{0}'.format(opt), action='count',
                                help='See `sphinx-build -h`')
        else:
            parser.add_argument('-{0}'.format(opt), action='append',
                                metavar=meta, help='See `sphinx-build -h`')

    parser.add_argument('sourcedir')
    parser.add_argument('outdir')
    parser.add_argument('filenames', nargs='*', help='See `sphinx-build -h`')
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)

    build_args = []
    for arg, meta in SPHINX_BUILD_OPTIONS:
        val = getattr(args, arg)
        if not val:
            continue
        opt = '-{0}'.format(arg)
        if meta is None:
            build_args.extend([opt] * val)
        else:
            for v in val:
                build_args.extend([opt, v])

    build_args.extend([srcdir, outdir])
    build_args.extend(args.filenames)

    ignored = args.ignore
    if args.w:  # Logfile
        ignored.append(os.path.realpath(args.w[0]))
    if args.d:  # Doctrees
        ignored.append(os.path.realpath(args.d[0]))

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    re_ignore = args.re_ignore + DEFAULT_IGNORE_REGEX

    if args.port != 0:
        portn = args.port
    else:
        portn = port_for.select_random()

    event_action_data = EventActionData()

    builder = SphinxBuilder(outdir, build_args, ignored, re_ignore)
    watcher = LivereloadWatchdogWatcher(event_action_data,
                                        use_polling=args.use_polling)
    action_thread = EventActionThread(
        event_action_data, action=builder, watcher=watcher,
        check_interval=args.event_delay)

    server = Server(watcher=watcher)
    action_thread.start()

    server.watch(srcdir, builder)
    for dirpath in args.additional_watched_dirs:
        dirpath = os.path.realpath(dirpath)
        server.watch(dirpath, builder)
    server.watch(outdir)

    if args.initial_build:
        builder.build()

    if args.openbrowser is True:
        server.serve(port=portn, host=args.host,
                     root=outdir, open_url_delay=args.delay)
    else:
        server.serve(port=portn, host=args.host, root=outdir)

    try:
        action_thread.kill()
        action_thread.join()
    except KeyboardInterrupt:
        pass
