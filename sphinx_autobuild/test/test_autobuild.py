"""
sphinx-autobuild tests.
"""

import mock
import pytest
import livereload
from watchdog import observers

from sphinx_autobuild import main


@pytest.fixture(autouse=True)
def patched_args(sys_args, monkeypatch):
    """Patch sys args."""
    monkeypatch.setattr('sys.argv', sys_args)


@pytest.mark.parametrize('sys_args', (
    ['sphinx-autobuild', '/source', '/output'],
))
@mock.patch.object(observers.Observer, 'schedule')
@mock.patch.object(livereload.Server, 'serve')
@mock.patch('os.makedirs')
def test_autobuild(mock_makedirs, mock_serve, mock_schedule):
    """
    Test autobuild entry point.
    """
    main()
    mock_makedirs.assert_called_once_with('/output')
    mock_serve.assert_called_once_with(
        host='127.0.0.1', root='/output', port=8000)
