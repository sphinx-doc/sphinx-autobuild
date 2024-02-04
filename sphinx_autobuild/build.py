"""Logic for interacting with sphinx-build."""

import shlex
import subprocess
import sys

from colorama import Fore, Style


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


class Builder:
    def __init__(self, watcher, sphinx_args, *, host, port, pre_build_commands):
        self.watcher = watcher
        self.sphinx_args = sphinx_args
        self.pre_build_commands = pre_build_commands
        self.uri = f"http://{host}:{port}"

    def __call__(self):
        """Generate the documentation using ``sphinx``."""

        sphinx_command = [sys.executable, "-m", "sphinx"] + self.sphinx_args

        if self.watcher.filepath:
            show(context=f"Detected change: {self.watcher.filepath}")

        try:
            for command in self.pre_build_commands:
                show(context="pre-build", command=command)
                subprocess.run(command, check=True)

            show(command=["sphinx-build"] + self.sphinx_args)
            subprocess.run(sphinx_command, check=True)
        except subprocess.CalledProcessError as e:
            self.cmd_exit(e.returncode)
        finally:
            # We present this information, so that the user does not need to keep track
            # of the port being used. It is presented by livereload when starting the
            # server, so don't present it in the initial build.
            if self.watcher.filepath:
                show(context=f"Serving on {self.uri}")

    @staticmethod
    def cmd_exit(return_code):
        print(f"Command exited with exit code: {return_code}")
        print(
            "The server will continue serving the build folder, but the contents "
            "being served are no longer in sync with the documentation sources. "
            "Please fix the cause of the error above or press Ctrl+C to stop the "
            "server."
        )
