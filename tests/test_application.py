"""A very basic test that the application works."""

import shutil
from pathlib import Path

import anyio
import httpx
import pytest
from asgi_lifespan import LifespanManager
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from sphinx_autobuild.__main__ import _create_app
from sphinx_autobuild.build import Builder
from sphinx_autobuild.filter import IgnoreFilter

ROOT = Path(__file__).parent.parent


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_application(tmp_path, anyio_backend):  # noqa: ARG001
    src_dir = tmp_path / "docs"
    out_dir = tmp_path / "build"
    shutil.copytree(ROOT / "docs", tmp_path / "docs")
    out_dir.mkdir(parents=True, exist_ok=True)
    index_file = anyio.Path(src_dir / "index.rst")
    await index_file.write_text("hello")

    url_host = "127.0.0.1:7777"
    ignore_handler = IgnoreFilter([out_dir], [])
    builder = Builder(
        [str(src_dir), str(out_dir)],
        url_host=url_host,
        pre_build_commands=[],
        post_build_commands=[],
    )
    app = _create_app([src_dir], ignore_handler, builder, out_dir, url_host)

    async with (
        LifespanManager(app) as manager,
        httpx.AsyncClient(
            transport=ASGIWebSocketTransport(manager.app), base_url="http://testserver"
        ) as client,
    ):
        builder(changed_paths=())

        response = await client.get("/")
        assert response.status_code == 200

        async with aconnect_ws("/websocket-reload", client) as websocket:
            await index_file.write_text("world")

            data = await websocket.receive_text()
            assert data == "refresh"
