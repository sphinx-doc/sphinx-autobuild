"""Logic for ignoring paths."""
import fnmatch
import os
import re


def get_ignore(regular_patterns, regex_based):
    """Prepare the function that determines whether a path should be ignored."""
    regex_based_patterns = list(map(re.compile, regex_based))

    def ignore(path):
        """Determine if path should be ignored."""
        # Any regular pattern matches.
        for pattern in regular_patterns:
            if path.startswith((pattern + os.sep, pattern + "/")):
                return True
            if fnmatch.fnmatch(path, pattern):
                return True

        # Any regular expression matches.
        for regex in regex_based_patterns:
            if regex.search(path):
                return True

        return False

    return ignore
