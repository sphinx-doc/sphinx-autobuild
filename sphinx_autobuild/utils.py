"""Generic utilities."""

from __future__ import annotations

import shlex
import socket

from colorama import Fore, Style


def find_free_port():
    """Find and return a free port number.

    Shout-out to https://stackoverflow.com/a/45690594/1931274!
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def _log(text, *, colour):
    print(f"{Fore.GREEN}[sphinx-autobuild] {colour}{text}{Style.RESET_ALL}")


def show_message(context: str, /) -> None:
    """Show context, with nice formatting and colours."""
    _log(context, colour=Fore.CYAN)


def show_command(command: list[str] | tuple[str, ...], /) -> None:
    """Show command-to-be-executed, with nice formatting and colours."""
    assert isinstance(command, (list, tuple))
    msg = f"> {shlex.join(command)}"
    _log(msg, colour=Fore.BLUE)
