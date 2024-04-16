"""Logic for interacting with sphinx-build."""

import subprocess

# This isn't public API, but we want to avoid a subprocess call
from sphinx.cmd.build import build_main

from sphinx_autobuild.utils import show


class Builder:
    def __init__(self, sphinx_args, *, url_host, pre_build_commands):
        self.sphinx_args = sphinx_args
        self.pre_build_commands = pre_build_commands
        self.uri = f"http://{url_host}"

    def __call__(self, *, rebuild: bool = True):
        """Generate the documentation using ``sphinx``."""
        if rebuild:
            show(context="Detected change. Rebuilding...")

        try:
            for command in self.pre_build_commands:
                show(context="pre-build", command=command)
                subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Pre-build command exited with exit code: {e.returncode}")
            print(
                "Please fix the cause of the error above or press Ctrl+C to stop the "
                "server."
            )
            raise

        show(command=["sphinx-build"] + self.sphinx_args)

        # NOTE:
        # sphinx.cmd.build.build_main is not considered to be public API,
        # but as this is a first-party project, we can cheat a little bit.
        if return_code := build_main(self.sphinx_args):
            print(f"Sphinx exited with exit code: {return_code}")
            print(
                "The server will continue serving the build folder, but the contents "
                "being served are no longer in sync with the documentation sources. "
                "Please fix the cause of the error above or press Ctrl+C to stop the "
                "server."
            )
        # Remind the user of the server URL for convenience.
        show(context=f"Serving on {self.uri}")
