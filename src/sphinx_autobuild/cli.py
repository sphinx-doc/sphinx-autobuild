"""Main implementation."""

import argparse
import os

from livereload import Server

from . import __version__
from .sphinx import SPHINX_BUILD_OPTIONS, SphinxBuilder
from .watcher import LivereloadWatchdogWatcher
from .utils import find_free_port

DEFAULT_IGNORE_REGEX = [r".*\.pyc"]


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
    if not os.path.exists(outdir):
        os.makedirs(outdir)

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

    re_ignore = args.re_ignore + DEFAULT_IGNORE_REGEX

    # Find the free port
    portn = args.port or find_free_port()

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
