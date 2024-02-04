"""Logic for interacting with sphinx-build."""

import shlex
import subprocess
import sys

from colorama import Fore, Style

SPHINX_BUILD_OPTIONS = (
    # general options
    ("-b", "builder"),
    ("-a", None),
    ("-E", None),
    ("-j", "N"),
    ("--jobs", "N"),
    # path options
    ("-d", "path"),
    ("-c", "path"),
    # build configuration options
    ("-C", None),
    ("-D", "setting=value"),
    ("-A", "name=value"),
    ("-t", "tag"),
    ("-n", None),
    # console output options
    ("-v", None),
    ("-q", None),
    ("-Q", None),
    ("--color", None),
    ("-N", None),
    # warning control options
    ("-w", "file"),
    ("--keep-going", None),
    ("-W", None),
    ("-T", None),
    ("-P", None),
)


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


def get_builder(watcher, sphinx_args, *, host, port, pre_build_commands):
    """Prepare the function that calls sphinx."""
    sphinx_command = [sys.executable, "-m", "sphinx"] + sphinx_args

    def build():
        """Generate the documentation using ``sphinx``."""
        if watcher.filepath:
            show(context=f"Detected change: {watcher.filepath}")

        try:
            for command in pre_build_commands:
                show(context="pre-build", command=command)
                subprocess.run(command, check=True)

            show(command=["sphinx-build"] + sphinx_args)
            subprocess.run(sphinx_command, check=True)
        except subprocess.CalledProcessError as e:
            cmd_exit(e.returncode)
        finally:
            # We present this information, so that the user does not need to keep track
            # of the port being used. It is presented by livereload when starting the
            # server, so don't present it in the initial build.
            if watcher.filepath:
                show(context=f"Serving on http://{host}:{port}")

    return build


def cmd_exit(return_code):
    print(f"Command exited with exit code: {return_code}")
    print(
        "The server will continue serving the build folder, but the contents "
        "being served are no longer in sync with the documentation sources. "
        "Please fix the cause of the error above or press Ctrl+C to stop the "
        "server."
    )
