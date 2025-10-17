"""A very basic test that the application works."""

import shutil
import socket
from pathlib import Path

from starlette.testclient import TestClient

from sphinx_autobuild.__main__ import _create_app
from sphinx_autobuild.build import Builder
from sphinx_autobuild.filter import IgnoreFilter
from sphinx_autobuild.utils import find_free_port, is_port_available

ROOT = Path(__file__).parent.parent


def test_application(tmp_path):
    src_dir = tmp_path / "docs"
    out_dir = tmp_path / "build"
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    out_dir.mkdir(parents=True, exist_ok=True)

    url_host = "127.0.0.1:7777"
    ignore_handler = IgnoreFilter([out_dir], [])
    builder = Builder(
        [str(src_dir), str(out_dir)],
        url_host=url_host,
        pre_build_commands=[],
        post_build_commands=[],
    )
    app = _create_app([src_dir], ignore_handler, builder, out_dir, url_host)
    client = TestClient(app)

    builder(changed_paths=())

    response = client.get("/")
    assert response.status_code == 200


def test_is_port_available():
    """Test that is_port_available correctly detects available and unavailable ports."""
    # A high port number should generally be available
    high_port = find_free_port()
    assert is_port_available("127.0.0.1", high_port)

    # Bind a port and verify is_port_available detects it as unavailable
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    test_port = find_free_port()
    s.bind(("127.0.0.1", test_port))

    try:
        # Now the port should not be available
        assert not is_port_available("127.0.0.1", test_port)

        # A different high port should still be available
        other_port = find_free_port()
        assert other_port != test_port
        assert is_port_available("127.0.0.1", other_port)
    finally:
        s.close()
