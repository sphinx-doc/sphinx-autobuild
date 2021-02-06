"""Main implementation."""

from . import _hacks  # isort:skip  # noqa

import argparse
import os
import shlex

import colorama
from livereload import Server

from . import __version__
from .build import SPHINX_BUILD_OPTIONS, get_builder
from .ignore import get_ignore
from .utils import find_free_port


def _get_build_args(args):
    build_args = []
    for arg, meta in SPHINX_BUILD_OPTIONS:
        val = getattr(args, arg)
        if not val:
            continue
        opt = f"-{arg}"
        if meta is None:
            build_args.extend([opt] * val)
        else:
            for v in val:
                build_args.extend([opt, v])

    build_args.extend([os.path.realpath(args.sourcedir), os.path.realpath(args.outdir)])
    build_args.extend(args.filenames)

    pre_build_commands = [shlex.split(cmd_str) for cmd_str in args.pre_build]
    return build_args, pre_build_commands


def _get_ignore_handler(args):
    regular = args.ignore[:]
    regular.append(os.path.realpath(args.outdir))  # output directory
    if args.w:  # Logfile
        regular.append(os.path.realpath(args.w[0]))
    if args.d:  # Doctrees
        regular.append(os.path.realpath(args.d[0]))

    regex_based = args.re_ignore
    return get_ignore(regular, regex_based)


def get_parser():
    """Get the application's argument parser.

    Note: this also handles SPHINX_BUILD_OPTIONS, which later get forwarded to
    sphinx-build as-is.
    """

    class RawTextArgumentDefaultsHelpFormatter(
        argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter
    ):
        pass

    parser = argparse.ArgumentParser(
        formatter_class=RawTextArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port to serve documentation on. 0 means find and use a free port",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="hostname to serve documentation on",
    )
    parser.add_argument(
        "--re-ignore",
        action="append",
        default=[],
        help="regular expression for files to ignore, when watching for changes",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="glob expression for files to ignore, when watching for changes",
    )
    parser.add_argument(
        "--no-initial",
        dest="no_initial_build",
        action="store_true",
        default=False,
        help="skip the initial build",
    )
    parser.add_argument(
        "--open-browser",
        dest="openbrowser",
        action="store_true",
        default=False,
        help="open the browser after building documentation",
    )
    parser.add_argument(
        "--delay",
        dest="delay",
        type=int,
        default=5,
        help="how long to wait before opening the browser",
    )
    parser.add_argument(
        "--watch",
        action="append",
        metavar="DIR",
        default=[],
        help="additional directories to watch",
        dest="additional_watched_dirs",
    )
    parser.add_argument(
        "--pre-build",
        action="append",
        metavar="COMMAND",
        default=[],
        help="additional command(s) to run prior to building the documentation",
    )
    parser.add_argument(
        "--version", action="version", version="sphinx-autobuild {}".format(__version__)
    )

    sphinx_arguments = ", ".join(
        f"-{arg}" if meta is None else f"-{arg}={meta}"
        for arg, meta in SPHINX_BUILD_OPTIONS
    )
    sphinx_parser = parser.add_argument_group(
        "sphinx's arguments",
        (
            "The following arguments are forwarded as-is to Sphinx. Please look at "
            f"`sphinx --help` for more information.\n  {sphinx_arguments}"
        ),
    )

    for arg, meta in SPHINX_BUILD_OPTIONS:
        if meta is None:
            sphinx_parser.add_argument(
                f"-{arg}", action="count", help=argparse.SUPPRESS
            )
        else:
            sphinx_parser.add_argument(
                f"-{arg}", action="append", help=argparse.SUPPRESS, metavar=meta,
            )

    parser.add_argument("sourcedir", help="source directory")
    parser.add_argument("outdir", help="output directory for built documentation")
    parser.add_argument(
        "filenames", nargs="*", help="specific files to rebuild on each run"
    )
    return parser


def main():
    """Actual application logic."""
    colorama.init()

    parser = get_parser()
    args = parser.parse_args()

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    portn = args.port or find_free_port()
    server = Server()

    build_args, pre_build_commands = _get_build_args(args)
    builder = get_builder(
        server.watcher,
        build_args,
        host=args.host,
        port=portn,
        pre_build_commands=pre_build_commands,
    )

    ignore_handler = _get_ignore_handler(args)
    server.watch(srcdir, builder, ignore=ignore_handler)
    for dirpath in args.additional_watched_dirs:
        dirpath = os.path.realpath(dirpath)
        server.watch(dirpath, builder, ignore=ignore_handler)
    server.watch(outdir, ignore=ignore_handler)

    if not args.no_initial_build:
        builder()

    if args.openbrowser is True:
        server.serve(port=portn, host=args.host, root=outdir, open_url_delay=args.delay)
    else:
        server.serve(port=portn, host=args.host, root=outdir)
