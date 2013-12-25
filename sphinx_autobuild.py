"""
Sphinx Documentation Automatic Builder

MIT License. See LICENSE for more details.
Copyright (c) 2013, Jonathan Stoppani
"""


import argparse
import os
import subprocess
import sys
import pty
import multiprocessing

from livereload import Server

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


__version__ = '0.1.0'


class _WatchdogHandler(FileSystemEventHandler):

    def __init__(self, watcher, action):
        super(_WatchdogHandler, self).__init__()
        self._watcher = watcher
        self._action = action

    def on_any_event(self, event):
        if event.is_directory:
            return
        self._action(self._watcher, event.src_path)


class LivereloadWatchdogWatcher(object):

    def __init__(self):
        super(LivereloadWatchdogWatcher, self).__init__()
        self._changed = False
        self._action_file = None  # TODO: Hack
        self._observer = Observer()
        self._observer.start()

        # Compatibility with livereload's builtin watcher
        self._tasks = True
        self.filepath = None

    def set_changed(self):
        self._changed = True

    def examine(self):
        if self._changed:
            self._changed = False
            return self._action_file or True  # TODO: Hack

    def watch(self, path, action=None):
        if action is None:
            action = lambda w, _: w.set_changed()
        event_handler = _WatchdogHandler(self, action)
        self._observer.schedule(event_handler, path=path, recursive=True)


class SphinxBuilder(object):

    def __init__(self, outdir, args):
        self._outdir = outdir
        self._args = args

    def __call__(self, watcher, src_path):
        path = self.get_relative_path(src_path)

        if src_path.startswith(self._outdir + os.sep):
            return

        watcher._action_file = path  # TODO: Hack

        master, slave = pty.openpty()
        stdout = os.fdopen(master)

        pre = '+--------- {} changed '.format(path)
        sys.stdout.write('\n')
        sys.stdout.write(pre)
        sys.stdout.write('-' * (81 - len(pre)))
        sys.stdout.write('\n')
        subprocess.Popen(['sphinx-build'] + self._args, stdout=slave)
        os.close(slave)
        while 1:
            line = stdout.readline()
            if not line:
                break
            sys.stdout.write('| ')
            sys.stdout.write(line.rstrip())
            sys.stdout.write('\n')
        sys.stdout.write('+')
        sys.stdout.write('-' * 80)
        sys.stdout.write('\n\n')

    def get_relative_path(self, path):
        return os.path.relpath(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8000)
    parser.add_argument('sourcedir')
    parser.add_argument('outdir')

    args, remaining = parser.parse_known_args()

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)

    remaining += ['-j', str(multiprocessing.cpu_count() + 1), srcdir, outdir]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    server = Server(watcher=LivereloadWatchdogWatcher())
    server.watch(srcdir, SphinxBuilder(outdir, remaining))
    server.watch(outdir)
    server.serve(port=args.port, root=outdir)
