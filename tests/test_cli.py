from argparse import Namespace
from unittest import mock
import tempfile
import os


def test__get_ignore_handler():
    args_ignore = ["ignore.pyc"]
    args_re_ignore = ["^REGEX1$", "^REGEX2$"]

    with mock.patch("sphinx_autobuild.ignore.get_ignore") as mock_get_ignore:
        from sphinx_autobuild.cli import _get_ignore_handler

        with tempfile.TemporaryDirectory() as tmpdir:
            args = Namespace(
                sourcedir=tmpdir,
                outdir="output/directory",
                ignore=args_ignore,
                re_ignore=args_re_ignore,
                w=['error.log'],
                d=['doctrees-cache'],
            )

            # without conf.py
            _get_ignore_handler(args)

            expected_ignore = [
                os.path.realpath("ignore.pyc"),
                os.path.realpath("output/directory"),
                os.path.realpath("error.log"),
                os.path.realpath("doctrees-cache"),
            ]
            expected_re_ignore = args_re_ignore

            mock_get_ignore.assert_called_once_with(expected_ignore, expected_re_ignore)

            mock_get_ignore.reset_mock()

            # with conf.py
            with open(os.path.join(tmpdir, "conf.py"), mode="w") as f:
                f.write("exclude_patterns = ['drafts/*.rst', 'drafts/*.md']")

            _get_ignore_handler(args)

            expected_ignore = [
                os.path.realpath("ignore.pyc"),
                os.path.realpath("output/directory"),
                os.path.realpath("error.log"),
                os.path.realpath("doctrees-cache"),
                os.path.realpath("drafts/*.rst"),
                os.path.realpath("drafts/*.md"),
            ]
            expected_re_ignore = args_re_ignore

            mock_get_ignore.assert_called_once_with(expected_ignore, expected_re_ignore)
