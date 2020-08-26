"""Main implementation."""

import argparse
import os

from livereload import Server

from . import __version__
from .ignore import IgnoreHandler
from .sphinx import SPHINX_BUILD_OPTIONS, get_builder
from .utils import find_free_port


def _get_build_args(args):
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

    build_args.extend([os.path.realpath(args.sourcedir), os.path.realpath(args.outdir)])
    build_args.extend(args.filenames)
    return build_args


def _get_ignore_handler(args):
    regular = args.ignore[:]
    regular.append(os.path.realpath(args.outdir))  # output directory
    if args.w:  # Logfile
        regular.append(os.path.realpath(args.w[0]))
    if args.d:  # Doctrees
        regular.append(os.path.realpath(args.d[0]))

    regex_based = args.re_ignore

    return IgnoreHandler(regular, regex_based)


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
        help="Specify additional directories to watch. May be used multiple times.",
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

    ignore_handler = _get_ignore_handler(args)
    build_args = _get_build_args(args)

    builder = get_builder(build_args)
    server = Server()

    server.watch(srcdir, builder, ignore=ignore_handler)
    for dirpath in args.additional_watched_dirs:
        dirpath = os.path.realpath(dirpath)
        server.watch(dirpath, builder, ignore=ignore_handler)
    server.watch(outdir, ignore=ignore_handler)

    if args.initial_build:
        builder(initial=True)

    # Find the free port
    portn = args.port or find_free_port()
    if args.openbrowser is True:
        server.serve(port=portn, host=args.host, root=outdir, open_url_delay=args.delay)
    else:
        server.serve(port=portn, host=args.host, root=outdir)
