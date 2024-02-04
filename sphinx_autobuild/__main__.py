"""Entrypoint for ``python -m sphinx_autobuild``."""

from sphinx_autobuild import _hacks  # isort:skip  # noqa

import argparse
import os
import shlex
import sys

import colorama
from livereload import Server

# This isn't public API, but there aren't many better options
from sphinx.cmd.build import get_parser as sphinx_get_parser

from sphinx_autobuild import __version__
from sphinx_autobuild.build import Builder
from sphinx_autobuild.ignore import Ignore
from sphinx_autobuild.utils import find_free_port


def main():
    """Actual application logic."""
    colorama.init()

    args, build_args = _parse_args(sys.argv[1:])

    srcdir = os.path.realpath(args.sourcedir)
    outdir = os.path.realpath(args.outdir)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    port_num = args.port or find_free_port()
    server = Server()

    pre_build_commands = list(map(shlex.split, args.pre_build))
    builder = Builder(
        server.watcher,
        build_args,
        host=args.host,
        port=port_num,
        pre_build_commands=pre_build_commands,
    )

    ignore_handler = _get_ignore_handler(
        args.ignore, args.re_ignore, outdir, args.warnings_file, args.doctree_dir
    )
    server.watch(srcdir, builder, ignore=ignore_handler)
    for dirpath in args.additional_watched_dirs:
        dirpath = os.path.realpath(dirpath)
        server.watch(dirpath, builder, ignore=ignore_handler)
    server.watch(outdir, ignore=ignore_handler)

    if not args.no_initial_build:
        builder()

    if args.openbrowser is True:
        server.serve(
            port=port_num, host=args.host, root=outdir, open_url_delay=args.delay
        )
    else:
        server.serve(port=port_num, host=args.host, root=outdir)


def _parse_args(argv):
    # Parse once with the Sphinx parser to emit errors
    # and capture the ``-d`` and ``-w`` options.
    # NOTE:
    # The Sphinx parser is not considered to be public API,
    # but as this is a first-party project, we can cheat a little bit.
    sphinx_args = _get_sphinx_build_parser().parse_args(argv.copy())
    print(f"{sphinx_args.filenames=}")

    # Parse a second time with just our parser
    parser = _get_parser()
    args, build_args = parser.parse_known_args(argv.copy())

    # Copy needed settings
    args.sourcedir = sphinx_args.sourcedir
    args.outdir = sphinx_args.outputdir
    args.doctree_dir = sphinx_args.doctreedir
    args.warnings_file = sphinx_args.warnfile

    return args, build_args


def _get_sphinx_build_parser():
    # NOTE:
    # sphinx.cmd.build.get_parser is not considered to be public API,
    # but as this is a first-party project, we can cheat a little bit.
    sphinx_build_parser = sphinx_get_parser()
    sphinx_build_parser.description = None
    sphinx_build_parser.epilog = None
    sphinx_build_parser.prog = "sphinx-autobuild"
    for action in sphinx_build_parser._actions:
        if hasattr(action, "version"):
            # Fix the version
            action.version = f"%(prog)s {__version__}"
            break
    _add_autobuild_arguments(sphinx_build_parser)

    return sphinx_build_parser


def _get_parser():
    """Get the application's argument parser."""

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument(
        "--version", action="version", version=f"sphinx-autobuild {__version__}"
    )
    _add_autobuild_arguments(parser)

    return parser


def _add_autobuild_arguments(parser):
    group = parser.add_argument_group("autobuild options")
    group.add_argument(
        "--port",
        type=int,
        default=8000,
        help="port to serve documentation on. 0 means find and use a free port",
    )
    group.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="hostname to serve documentation on",
    )
    group.add_argument(
        "--re-ignore",
        action="append",
        default=[],
        help="regular expression for files to ignore, when watching for changes",
    )
    group.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="glob expression for files to ignore, when watching for changes",
    )
    group.add_argument(
        "--no-initial",
        dest="no_initial_build",
        action="store_true",
        default=False,
        help="skip the initial build",
    )
    group.add_argument(
        "--open-browser",
        dest="openbrowser",
        action="store_true",
        default=False,
        help="open the browser after building documentation",
    )
    group.add_argument(
        "--delay",
        dest="delay",
        type=int,
        default=5,
        help="how long to wait before opening the browser",
    )
    group.add_argument(
        "--watch",
        action="append",
        metavar="DIR",
        default=[],
        help="additional directories to watch",
        dest="additional_watched_dirs",
    )
    group.add_argument(
        "--pre-build",
        action="append",
        metavar="COMMAND",
        default=[],
        help="additional command(s) to run prior to building the documentation",
    )
    return group


def _get_ignore_handler(ignore, regex_based, out_dir, doctree_dir, warnings_file):
    regular = list(map(os.path.realpath, ignore))
    regular.append(os.path.realpath(out_dir))  # output directory
    if doctree_dir:  # Doctrees
        regular.append(os.path.realpath(doctree_dir))
    if warnings_file:  # Logfile
        regular.append(os.path.realpath(warnings_file))

    return Ignore(regular, regex_based)


if __name__ == "__main__":
    main()
