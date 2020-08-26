"""Logic for interacting with sphinx-build."""

import sys

from .utils import run_with_surrounding_separators

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


def get_builder(args):
    """Prepare the function that calls sphinx."""
    command = [sys.executable, "-m", "sphinx"] + args

    def build(initial=False):
        """Generate the documentation using ``sphinx``."""
        heading = "initial build" if initial else "changes detected"
        run_with_surrounding_separators(command, heading=heading)

    return build
