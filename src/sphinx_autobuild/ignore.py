"""Logic for ignoring paths."""
import fnmatch
import re
from glob import glob
from os.path import abspath, sep


def get_ignore(regular, regex_based):
    """Prepare the function that determines whether a path should be ignored."""
    regular_patterns = regular
    regex_based_patterns = [re.compile(r) for r in regex_based]

    def ignore(path):
        """Determine if path should be ignored."""
        # Return the full path so we make sure we handle relative paths OK
        path_expanded = abspath(path)

        # Any regular pattern and glob matches
        for pattern in regular_patterns:
            # Expand the pattern into a list of files that match a glob
            matched_files = [abspath(ii) for ii in glob(pattern, recursive=True)]

            # If this file matches any of the glob matches, we ignore it
            if path_expanded in matched_files:
                return True

            # If the parent of this path matches any of the glob matches, ignore it
            if any(path_expanded.startswith(imatch) for imatch in matched_files):
                return True

            # These two checks are for preserving old behavior.
            # They might not be necessary but leaving here just in case.
            # Neither depends on the files actually being on disk.
            if fnmatch.fnmatch(path, pattern):
                return True
            if path.strip(sep).startswith(pattern.strip(sep)):
                return True

        # Any regular expression matches.
        for regex in regex_based_patterns:
            if regex.search(path):
                return True

        return False

    return ignore
