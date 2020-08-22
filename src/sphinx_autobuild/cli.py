"""Main implementation."""

try:
    import pty
except ImportError:
    pty = None

import argparse
import fnmatch
import os
import re
import subprocess
import sys

import port_for
from livereload import Server

from . import __version__
from .watcher import LivereloadWatchdogWatcher

DEFAULT_IGNORE_REGEX = [
    r"__pycache__/.*\.py",
    r".*\.pyc",
    r".*\.kate-swp",
]


class SphinxBuilder(object):
    """Helper class to run sphinx-build command."""

    def __init__(self, outdir, args, ignored=None, regex_ignored=None):
        """Prepare a new instance.

        Currently, the arguments are undocumented.
        """
        self._outdir = outdir
        self._args = args
        self._ignored = ignored or []
        self._ignored.append(outdir)
        self._regex_ignored = [re.compile(r) for r in regex_ignored or []]

    def is_ignored(self, src_path):
        """Determine if changes in src_path should be ignored."""
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
        """Build documentation, unless given path should be ignored."""
        path = self.get_relative_path(src_path)

        if self.is_ignored(src_path):
            return

        watcher._action_file = path  # TODO: Hack (see above)

        self.build(path)

    def build(self, path=None):
        """Perform a build using ``sphinx-build``."""
        if path:
            pre = "+--------- {0} changed ".format(path)
        else:
            pre = "+--------- manually triggered build "
        sys.stdout.write("\n")
        sys.stdout.write(pre)
        sys.stdout.write("-" * (81 - len(pre)))
        sys.stdout.write("\n")

        args = ["sphinx-build"] + self._args
        if pty:
            master, slave = pty.openpty()
            stdout = os.fdopen(master)
            subprocess.Popen(args, stdout=slave)
            os.close(slave)
        else:
            stdout = subprocess.Popen(
                args, stdout=subprocess.PIPE, universal_newlines=True
            ).stdout
        try:
            while 1:
                line = stdout.readline()
                if not line:
                    break
                sys.stdout.write("| ")
                sys.stdout.write(line.rstrip())
                sys.stdout.write("\n")
        except IOError:
            pass
        finally:
            if not pty:
                stdout.close()
        sys.stdout.write("+")
        sys.stdout.write("-" * 80)
        sys.stdout.write("\n\n")

    def get_relative_path(self, path):
        """Get the relative path."""
        return os.path.relpath(path)


SPHINX_BUILD_OPTIONS = (
    ("b", "builder"),
    ("a", None),
    ("E", None),
    ("d", "path"),
    ("j", "N"),
    ("c", "path"),
    ("C", None),
    ("D", "setting=value"),
    ("t", "tag"),
    ("A", "name=value"),
    ("n", None),
    ("v", None),
    ("q", None),
    ("Q", None),
    ("w", "file"),
    ("W", None),
    ("T", None),
    ("N", None),
    ("P", None),
)


def get_parser():
    """Get the application's argument parser.

    Note: this also handles SPHINX_BUILD_OPTIONS, which later get forwarded to
    sphinx-build as-is.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8000)
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1")
    parser.add_argument("-r", "--re-ignore", action="append", default=[])
    parser.add_argument("-i", "--ignore", action="append", default=[])
    parser.add_argument(
        "--poll", dest="use_polling", action="store_true", default=False
    )
    parser.add_argument(
        "--no-initial", dest="initial_build", action="store_false", default=True
    )
    parser.add_argument(
        "-B", "--open-browser", dest="openbrowser", action="store_true", default=False
    )
    parser.add_argument("-s", "--delay", dest="delay", type=int, default=5)
    parser.add_argument(
        "-z",
        "--watch",
        action="append",
        metavar="DIR",
        default=[],
        help=(
            "Specify additional directories to watch. May be" " used multiple times."
        ),
        dest="additional_watched_dirs",
    )
    parser.add_argument(
        "--version", action="version", version="sphinx-autobuild {}".format(__version__)
    )

    for opt, meta in SPHINX_BUILD_OPTIONS:
        if meta is None:
            parser.add_argument(
                "-{0}".format(opt), action="count", help="See `sphinx-build -h`"
            )
        else:
            parser.add_argument(
                "-{0}".format(opt),
                action="append",
                metavar=meta,
                help="See `sphinx-build -h`",
            )

    parser.add_argument("sourcedir")
    parser.add_argument("outdir")
    parser.add_argument("filenames", nargs="*", help="See `sphinx-build -h`")
    return parser


def main():
    """Actual application logic."""
    parser = get_parser()
    args = parser.parse_args()

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)

    build_args = []
    for arg, meta in SPHINX_BUILD_OPTIONS:
        val = getattr(args, arg)
        if not val:
            continue
        opt = "-{0}".format(arg)
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

    builder = SphinxBuilder(outdir, build_args, ignored, re_ignore)
    server = Server(watcher=LivereloadWatchdogWatcher(use_polling=args.use_polling),)

    server.watch(srcdir, builder)
    for dirpath in args.additional_watched_dirs:
        dirpath = os.path.realpath(dirpath)
        server.watch(dirpath, builder)
    server.watch(outdir)

    if args.initial_build:
        builder.build()

    if args.openbrowser is True:
        server.serve(port=portn, host=args.host, root=outdir, open_url_delay=args.delay)
    else:
        server.serve(port=portn, host=args.host, root=outdir)
