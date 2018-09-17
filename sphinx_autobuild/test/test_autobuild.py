"""
sphinx-autobuild tests.
"""

import mock
import pytest
import livereload
from mock import call
from watchdog import observers

from sphinx_autobuild import main, DEFAULT_IGNORE_REGEX


@pytest.fixture(autouse=True)
def patched_args(sys_args, monkeypatch):
    """Patch sys args."""
    monkeypatch.setattr('sys.argv', sys_args)


@pytest.mark.parametrize('sys_args, with_script', (
    (['sphinx-autobuild', '/source', '/output'], False),
    (['sphinx-autobuild', '/source', '/output',
      '--exec_script', '/script'], True),
))
@mock.patch.object(observers.Observer, 'schedule')
@mock.patch.object(livereload.Server, 'serve')
@mock.patch('sphinx_autobuild.SphinxBuilder.execute_script')
@mock.patch('sphinx_autobuild.SphinxBuilder._build')
@mock.patch('os.makedirs')
def test_autobuild(mock_makedirs, mock_builder, mock_execute_script,
                   mock_serve, mock_schedule, with_script):
    """
    Test autobuild entry point.
    """
    main()
    mock_builder.assert_called_once_with(None)
    if with_script:
        mock_execute_script.assert_called_once_with()
    else:
        mock_execute_script.assert_not_called()
    mock_makedirs.assert_called_once_with('/output')
    mock_serve.assert_called_once_with(
        host='127.0.0.1', root='/output', port=8000)


@pytest.mark.parametrize('sys_args', (
    ['sphinx-autobuild', '/source', '/output',
     '--port', '8888',
     '--host', 'example.org',
     '--ignore', '/ignored',
     '--watch', '/external',
     '--exec_script', '/script'],
))
@mock.patch.object(observers.Observer, 'schedule')
@mock.patch.object(livereload.Server, 'serve')
@mock.patch('sphinx_autobuild.SphinxBuilder')
@mock.patch.object(livereload.Server, 'watch')
@mock.patch('os.makedirs')
def test_autobuild_with_options(mock_makedirs,
                                mock_watch, mock_builder,
                                mock_serve, mock_schedule):
    """
    Test autobuild entry point with host, ignore, and watch options
    """
    main()
    mock_makedirs.assert_called_once_with('/output')

    # --port, --host
    mock_serve.assert_called_once_with(
        host='example.org', root='/output', port=8888)

    # --ignore
    mock_builder.assert_called_once_with(
        '/output', ['/source', '/output'], ['/ignored'],
        DEFAULT_IGNORE_REGEX, '/script')

    # --watch
    calls = [call('/source', mock_builder.return_value),
             call('/external', mock_builder.return_value),
             call('/output')]
    for call_spec in mock_watch.call_args_list:
        assert call_spec in calls
