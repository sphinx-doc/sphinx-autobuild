"""Logic for interacting with sphinx-build."""

import os
import sys
import subprocess

from .utils import run_with_surrounding_separators


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
            heading = "{0} changed".format(path)
        else:
            heading = "manually triggered build"

        args = [sys.executable, '-m', 'sphinx'] + self._args
        run_with_surrounding_separators(args, heading=heading)

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
