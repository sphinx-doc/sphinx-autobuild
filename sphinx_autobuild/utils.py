"""Generic utilities."""

import shlex
import socket
import threading
import time
import webbrowser

from colorama import Fore, Style


def find_free_port():
    """Find and return a free port number.

    Shout-out to https://stackoverflow.com/a/45690594/1931274!
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def open_browser(url_host: str, delay: float) -> None:
    def _opener():
        time.sleep(delay)
        webbrowser.open(f"http://{url_host}")

    t = threading.Thread(target=_opener)
    t.start()
    t.join()


def _log(text, *, colour):
    print(f"{Fore.GREEN}[sphinx-autobuild] {colour}{text}{Style.RESET_ALL}")


def show(*, context=None, command=None):
    """Show context and command-to-be-executed, with nice formatting and colours."""
    if context is not None:
        _log(context, colour=Fore.CYAN)
    if command is not None:
        assert isinstance(command, (list, tuple))
        msg = f"> {shlex.join(command)}"
        _log(msg, colour=Fore.BLUE)
