"""A very basic test that the application works."""

import shutil
from pathlib import Path

import pytest
from starlette.testclient import TestClient

from sphinx_autobuild.__main__ import _create_app
from sphinx_autobuild.build import Builder
from sphinx_autobuild.filter import IgnoreFilter

ROOT = Path(__file__).parent.parent


@pytest.mark.parametrize("path_prefix", ["", "/preview/docs"])
def test_application(tmp_path, path_prefix):
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
    app = _create_app(
        [src_dir], ignore_handler, builder, out_dir, url_host, path_prefix=path_prefix
    )
    client = TestClient(app)

    builder(changed_paths=())

    response = client.get(f"{path_prefix}/")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-cache"
    assert (
        f'new WebSocket("ws://{url_host}{path_prefix}/websocket-reload")'
        in response.text
    )
    assert client.get(f"{path_prefix}/_static/pygments.css").status_code == 200
    if path_prefix:
        assert client.get("/").status_code == 404

    with client.websocket_connect(f"{path_prefix}/websocket-reload"):
        pass
