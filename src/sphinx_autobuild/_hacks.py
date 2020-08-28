"""This file contains hacks needed to make things work. Ideally, this file is empty."""

from pathlib import PurePosixPath
from urllib.parse import urlparse

import livereload.server as server
from tornado.web import OutputTransform


# Why do we do this?
# See https://github.com/GaretJax/sphinx-autobuild/issues/71#issuecomment-681854580
class _FixedLiveScriptInjector(server.LiveScriptInjector):
    def __init__(self, request):
        # NOTE: Using super() here causes an infinite cycle, due to
        #       ConfiguredTransform not declaring an __init__.
        OutputTransform.__init__(self, request)

        # Determine if this is an HTML page
        path = PurePosixPath(urlparse(request.uri).path)
        self.should_modify_request = path.suffix in ["", ".html"]

    def transform_first_chunk(self, status_code, headers, chunk, finishing):
        if not self.should_modify_request:
            return status_code, headers, chunk
        return super().transform_first_chunk(status_code, headers, chunk, finishing)


server.LiveScriptInjector = _FixedLiveScriptInjector
