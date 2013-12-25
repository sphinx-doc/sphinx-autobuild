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

from livereload import Server

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


__version__ = '0.2.0'


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


sphinx_build_options = (
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=8000)

    for opt, meta in sphinx_build_options:
        if meta is None:
            parser.add_argument('-{}'.format(opt), action='count',
                            help='See sphinx-build -h')
        else:
            parser.add_argument('-{}'.format(opt), action='append',
                                metavar=meta, help='See sphinx-build -h')

    parser.add_argument('sourcedir')
    parser.add_argument('outdir')
    parser.add_argument('filenames', nargs='*', help='See sphinx-build -h')

    args = parser.parse_args()

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)

    remaining= []
    for arg, meta in sphinx_build_options:
        val = getattr(args, arg)
        if val is None:
            continue
        opt = '-{}'.format(arg)
        if meta is None:
            remaining.extend([opt] * val)
        else:
            for v in val:
                remaining.extend([opt, v])

    remaining.extend([srcdir, outdir])
    remaining.extend(args.filenames)

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    server = Server(watcher=LivereloadWatchdogWatcher())
    server.watch(srcdir, SphinxBuilder(outdir, remaining))
    server.watch(outdir)
    server.serve(port=args.port, root=outdir)
