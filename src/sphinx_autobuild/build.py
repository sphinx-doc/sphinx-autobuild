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


def get_builder(watcher, sphinx_args, *, pre_build_commands):
    """Prepare the function that calls sphinx."""
    sphinx_command = [sys.executable, "-m", "sphinx"] + sphinx_args

    def build():
        """Generate the documentation using ``sphinx``."""
        if watcher.filepath:
            heading = f"changed: {watcher.filepath}"
        else:
            heading = "manual build"

        for command in pre_build_commands:
            run_with_surrounding_separators(
                command, heading=f"pre-build for {heading}", include_footer=False
            )

        run_with_surrounding_separators(sphinx_command, heading=heading)

    return build
