"""Generic utilities."""

import socket
from contextlib import closing


def find_free_port():
    """Find and return a free port number.

    Shout-out to https://stackoverflow.com/a/45690594/1931274!
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
