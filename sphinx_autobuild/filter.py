"""Logic for ignoring paths."""

import fnmatch
import os
import re
from glob import glob


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
        # Return the full path so we make sure we handle relative paths OK
        path_expanded = os.path.abspath(path)
        # Any regular pattern matches.
        for pattern in self.regular_patterns:
            # Expand the pattern into a list of files that match a glob
            matched_files = set(map(os.path.abspath, glob(pattern, recursive=True)))

            if path_expanded in matched_files:
                return True

            # If the parent of this path matches any of the glob matches, ignore it
            if any(path_expanded.startswith(imatch) for imatch in matched_files):
                return True

            # These two checks are for preserving old behavior.
            # They might not be necessary but leaving here just in case.
            # Neither depends on the files actually being on disk.

            if path.strip(os.path.sep).startswith((
                pattern.strip(os.path.sep) + os.path.sep,
                pattern + "/",
            )):
                return True
            if fnmatch.fnmatch(path, pattern):
                return True

        # Any regular expression matches.
        for regex in self.regex_based_patterns:  # NoQA: SIM110
            if regex.search(path):
                return True

        return False
