"""Logic for interacting with sphinx-build."""

import os
import subprocess
import sys

try:
    import pty
except ImportError:
    pty = None


class SphinxBuilder(object):
    """Helper class to run sphinx-build command."""

    def __init__(self, args, ignore_handler):
        """Prepare a new instance.

        Currently, the arguments are undocumented.
        """
        self._args = args
        self._ignore_handler = ignore_handler

    def __call__(self, watcher, src_path):
        """Build documentation, unless given path should be ignored."""
        path = self.get_relative_path(src_path)

        if self._ignore_handler(src_path):
            return

        watcher._action_file = path  # TODO: Hack (see watcher.py)

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

        args = [sys.executable, '-m', 'sphinx'] + self._args
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
