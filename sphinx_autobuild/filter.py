"""Logic for ignoring paths."""

import fnmatch
import re
from pathlib import Path


class IgnoreFilter:
    def __init__(self, regular, regex_based):
        """Prepare the function that determines whether a path should be ignored."""
        normalised_paths = [Path(p).resolve().as_posix() for p in regular]
        self.regular_patterns = list(dict.fromkeys(normalised_paths))
        self.regex_based_patterns = [*map(re.compile, dict.fromkeys(regex_based))]

    def __repr__(self):
        return (
            f"IgnoreFilter(regular={self.regular_patterns!r}, "
            f"regex_based={self.regex_based_patterns!r})"
        )

    def __call__(self, path):
        """Determine if 'path' should be ignored."""
        path = Path(path).resolve().as_posix()
        # Any regular pattern matches.
        for pattern in self.regular_patterns:
            # separators are normalised before creating the IgnoreFilter
            if path.startswith(f"{pattern}/"):
                return True
            if fnmatch.fnmatch(path, pattern):
                return True

        # Any regular expression matches.
        for regex in self.regex_based_patterns:  # NoQA: SIM110
            if regex.search(path):
                return True

        return False
