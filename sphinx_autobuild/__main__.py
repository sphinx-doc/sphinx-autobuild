"""Entrypoint for ``python -m sphinx_autobuild``."""

import argparse
import os
import shlex
import sys

import colorama
import uvicorn

# This isn't public API, but there aren't many better options
from sphinx.cmd.build import get_parser as sphinx_get_parser
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles

from sphinx_autobuild import __version__
from sphinx_autobuild.build import Builder
from sphinx_autobuild.filter import IgnoreFilter
from sphinx_autobuild.middleware import JavascriptInjectorMiddleware
from sphinx_autobuild.server import RebuildServer
from sphinx_autobuild.utils import find_free_port, open_browser, show


def main():
    """Actual application logic."""
    colorama.init()

    args, build_args = _parse_args(sys.argv[1:])

    src_dir = args.sourcedir
    out_dir = args.outdir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    host_name = args.host
    port_num = args.port or find_free_port()
    url_host = f"{host_name}:{port_num}"

    pre_build_commands = list(map(shlex.split, args.pre_build))

    builder = Builder(
        build_args,
        url_host=url_host,
        pre_build_commands=pre_build_commands,
    )

    watch_dirs = [src_dir] + args.additional_watched_dirs
    ignore_handler = IgnoreFilter(
        [p for p in args.ignore + [out_dir, args.warnings_file, args.doctree_dir] if p],
        args.re_ignore,
    )
    watcher = RebuildServer(watch_dirs, ignore_handler, change_callback=builder)

    app = Starlette(
        routes=[
            WebSocketRoute("/websocket-reload", watcher, name="reload"),
            Mount("/", app=StaticFiles(directory=out_dir, html=True), name="static"),
        ],
        middleware=[Middleware(JavascriptInjectorMiddleware, ws_url=url_host)],
        lifespan=watcher.lifespan,
    )

    if not args.no_initial_build:
        show(context="Starting initial build")
        builder(rebuild=False)

    if args.open_browser:
        open_browser(url_host, args.delay)

    show(context="Waiting to detect changes...")
    try:
        uvicorn.run(app, host=host_name, port=port_num, log_level="warning")
    except KeyboardInterrupt:
        show(context="Server ceasing operations. Cheerio!")


def _parse_args(argv):
    # Parse once with the Sphinx parser to emit errors
    # and capture the ``-d`` and ``-w`` options.
    # NOTE:
    # The Sphinx parser is not considered to be public API,
    # but as this is a first-party project, we can cheat a little bit.
    sphinx_args = _get_sphinx_build_parser().parse_args(argv.copy())

    # Parse a second time with just our parser
    parser = _get_parser()
    args, build_args = parser.parse_known_args(argv.copy())

    # Copy needed settings
    args.sourcedir = os.path.realpath(sphinx_args.sourcedir)
    args.outdir = os.path.realpath(sphinx_args.outputdir)
    if sphinx_args.doctreedir:
        args.doctree_dir = os.path.realpath(sphinx_args.doctreedir)
    else:
        args.doctree_dir = None
    if sphinx_args.warnfile:
        args.warnings_file = os.path.realpath(sphinx_args.warnfile)
    else:
        args.warnings_file = None

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
        action="store_true",
        default=False,
        help="open the browser after building documentation",
    )
    group.add_argument(
        "--delay",
        dest="delay",
        type=float,
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


if __name__ == "__main__":
    main()
