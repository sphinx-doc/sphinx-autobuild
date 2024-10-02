"""Logic for interacting with sphinx-build."""

from __future__ import annotations

import subprocess
import sys

import sphinx

from sphinx_autobuild.utils import show_command, show_message


class Builder:
    def __init__(self, sphinx_args, *, url_host, pre_build_commands):
        self.sphinx_args = sphinx_args
        self.pre_build_commands = pre_build_commands
        self.uri = f"http://{url_host}"

    def __call__(self, *, rebuild: bool = True):
        """Generate the documentation using ``sphinx``."""
        if rebuild:
            show_message("Detected change. Rebuilding...")

        try:
            for command in self.pre_build_commands:
                show_message("pre-build")
                show_command(command)
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Pre-build command exited with exit code: {e.returncode}")
            print(
                "Please fix the cause of the error above or press Ctrl+C to stop the "
                "server."
            )
            raise

        if sphinx.version_info[:3] >= (7, 2, 3):
            sphinx_build_args = ["-m", "sphinx", "build"] + self.sphinx_args
        else:
            sphinx_build_args = ["-m", "sphinx"] + self.sphinx_args
        show_command(["python"] + sphinx_build_args)
        try:
            subprocess.run([sys.executable] + sphinx_build_args, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Sphinx exited with exit code: {e.returncode}")
            print(
                "The server will continue serving the build folder, but the contents "
                "being served are no longer in sync with the documentation sources. "
                "Please fix the cause of the error above or press Ctrl+C to stop the "
                "server."
            )
        # Remind the user of the server URL for convenience.
        show_message(f"Serving on {self.uri}")
