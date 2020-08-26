"""Logic for ignoring paths."""
import fnmatch
import os
import re


def get_ignore(regular, regex_based):
    """Prepare the function that determines whether a path should be ignored."""
    regular_patterns = regular
    regex_based_patterns = [re.compile(r) for r in regex_based]

    def ignore(path):
        """Determine if path should be ignored."""
        # Any regular pattern matches.
        for pattern in regular_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
            if path.startswith(pattern + os.sep):
                return True

        # Any regular expression matches.
        for regex in regex_based_patterns:
            if regex.search(path):
                return True

        return False

    return ignore
