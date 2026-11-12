"""A very basic test that the application works."""

import shutil
from pathlib import Path

from starlette.testclient import TestClient

from sphinx_autobuild.__main__ import _create_app
from sphinx_autobuild.build import Builder
from sphinx_autobuild.filter import IgnoreFilter

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
    assert response.headers["Cache-Control"] == "no-cache"


def test_range_request_not_injected(tmp_path):
    out_dir = tmp_path / "build"
    out_dir.mkdir()
    (out_dir / "index.html").write_bytes(b"<html><body>hello</body></html>")

    url_host = "127.0.0.1:7777"
    builder = Builder(
        [], url_host=url_host, pre_build_commands=[], post_build_commands=[]
    )
    app = _create_app([tmp_path], IgnoreFilter([], []), builder, out_dir, url_host)
    client = TestClient(app)

    response = client.get("/index.html", headers={"Range": "bytes=0-9"})
    assert response.status_code == 206
    assert response.headers["Content-Range"] == "bytes 0-9/31"
    assert response.headers["Content-Length"] == "10"
    assert response.content == b"<html><bod"

    # Full responses still get the reload script.
    response = client.get("/index.html")
    assert response.status_code == 200
    assert b"/websocket-reload" in response.content
