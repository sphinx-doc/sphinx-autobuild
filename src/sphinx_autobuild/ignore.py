"""Logic for ignoring paths."""
import fnmatch
import os
import re


class IgnoreHandler:
    """Encapsulates logic for ignoring paths based on user's inputs."""

    def __init__(self, regular, regex_based):
        """Prepare the IgnoreHandler."""
        super().__init__()

        self.regular = regular
        self.regex_based = [re.compile(r) for r in regex_based]

    def __call__(self, path):
        """Determine whether the given path should be ignored."""
        # Any regular pattern matches.
        for pattern in self.regular:
            if fnmatch.fnmatch(path, pattern):
                return True
            if path.startswith(pattern + os.sep):
                return True

        # Any regular expression matches.
        for regex in self.regex_based:
            if regex.search(path):
                return True

        return False
