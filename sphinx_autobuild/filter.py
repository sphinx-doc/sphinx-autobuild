"""Logic for ignoring paths."""

import fnmatch
import re


class IgnoreFilter:
    def __init__(self, regular, regex_based):
        """Prepare the function that determines whether a path should be ignored."""
        self.regular_patterns = [*dict.fromkeys(regular)]
        self.regex_based_patterns = [*map(re.compile, dict.fromkeys(regex_based))]

    def __repr__(self):
        return (
            f"IgnoreFilter(regular={self.regular_patterns!r}, "
            f"regex_based={self.regex_based_patterns!r})"
        )

    def __call__(self, path):
        """Determine if 'path' should be ignored."""
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
