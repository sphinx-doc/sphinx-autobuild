"""Check that browser opening follows server readiness."""

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sphinx_autobuild.__main__ import main


@pytest.fixture
def cli_args(tmp_path):
    source = tmp_path / "docs"
    source.mkdir()
    return [str(source), str(tmp_path / "build"), "--host", "localhost"]


@pytest.fixture
def builder(monkeypatch):
    builder = Mock()
    monkeypatch.setattr("sphinx_autobuild.__main__.Builder", Mock(return_value=builder))
    return builder


@pytest.fixture
def browser(monkeypatch):
    browser = Mock()
    monkeypatch.setattr("webbrowser.open", browser)
    return browser


@pytest.fixture
def server(monkeypatch):
    async def serve():
        await asyncio.sleep(0.01)

    server = SimpleNamespace(started=False, should_exit=False, serve=serve)
    monkeypatch.setattr("uvicorn.Server", Mock(return_value=server))
    return server


def test_browser_waits_for_server_and_delay(cli_args, browser, builder, server):
    # GIVEN
    ready_at = None
    loop = None
    opened = asyncio.Event()

    def open_browser(url):
        assert server.started
        assert url == "http://localhost:8000"
        assert time.monotonic() - ready_at >= 0.02
        loop.call_soon_threadsafe(opened.set)

    browser.side_effect = open_browser

    async def serve():
        nonlocal ready_at, loop
        loop = asyncio.get_running_loop()
        builder.assert_called_once_with(changed_paths=())
        # Startup takes longer than the requested browser delay.
        await asyncio.sleep(0.15)
        browser.assert_not_called()
        ready_at = time.monotonic()
        server.started = True
        await asyncio.wait_for(opened.wait(), timeout=2)

    server.serve = serve

    # WHEN
    main([*cli_args, "--open-browser", "--delay", "0.02"])

    # THEN
    browser.assert_called_once_with("http://localhost:8000")


@pytest.mark.usefixtures("builder")
@pytest.mark.parametrize(
    ("started", "delay", "should_exit"),
    [
        (False, 0, False),
        (True, 60, False),
        (True, None, False),
        (True, 0, True),
    ],
)
def test_browser_does_not_open_after_server_stops(
    cli_args, browser, server, started, delay, should_exit
):
    # GIVEN
    server.started = started
    server.should_exit = should_exit
    if delay is not None:
        cli_args.extend(["--open-browser", "--delay", str(delay)])

    # WHEN
    main(cli_args)

    # THEN
    browser.assert_not_called()


@pytest.mark.usefixtures("builder")
def test_browser_does_not_open_when_server_startup_fails(cli_args, browser, server):
    # GIVEN
    async def serve():
        await asyncio.sleep(0.01)
        raise RuntimeError("Startup failed")

    server.serve = serve

    # WHEN
    with pytest.raises(ExceptionGroup) as exc_info:
        main([*cli_args, "--open-browser", "--delay", "0"])

    # THEN
    assert len(exc_info.value.exceptions) == 1
    error = exc_info.value.exceptions[0]
    assert isinstance(error, RuntimeError)
    assert str(error) == "Startup failed"
    browser.assert_not_called()
