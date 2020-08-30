"""Generic utilities."""

import os
import socket
import subprocess
import sys
from contextlib import closing

try:
    import pty
except ImportError:
    have_pty = False
else:
    have_pty = True


def find_free_port():
    """Find and return a free port number.

    Shout-out to https://stackoverflow.com/a/45690594/1931274!
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def run_with_surrounding_separators(args, *, heading, include_footer=True):
    """Run a subprocess with the output surrounded by a box.

    Looks like::

        +---------- heading ----------
        | first line of output
        | second line of output
        +-----------------------------
    """
    separator_width = 80
    header = "+" + f"-- {heading} --".center(separator_width, "-")
    footer = "+" + "-" * separator_width

    sys.stdout.write(header + "\n")

    if have_pty:
        parent, child = pty.openpty()
        stdout = os.fdopen(parent)
        subprocess.Popen(args, stdout=child)
        os.close(child)
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
        if not have_pty:
            stdout.close()

    if include_footer:
        sys.stdout.write(footer + "\n")
