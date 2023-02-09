"""Logic for ignoring paths."""
import fnmatch
import re
from glob import glob
from os.path import abspath


def get_ignore(regular, regex_based):
    """Prepare the function that determines whether a path should be ignored."""
    regular_patterns = regular
    regex_based_patterns = [re.compile(r) for r in regex_based]

    def ignore(path):
        """Determine if path should be ignored."""
        # Return the full path so we make sure we handle relative paths OK
        path = abspath(path)

        # Any regular pattern and glob matches
        for pattern in regular_patterns:
            # Expand the pattern into a list of files that match a glob
            matched_files = [abspath(ii) for ii in glob(pattern, recursive=True)]

            # If this file matches any of the glob matches, we ignore it
            if path in matched_files:
                return True

            # If the parent of this path matches any of the glob matches, ignore it
            if any(path.startswith(imatch) for imatch in matched_files):
                return True

            # If fnmatch matches, then return True (to preserve old behavior)
            # This one doesn't depend on the files actually being present on disk.
            if fnmatch.fnmatch(path, pattern):
                return True

        # Any regular expression matches.
        for regex in regex_based_patterns:
            if regex.search(path):
                return True

        return False

    return ignore
