from glob import glob

from sphinx_autobuild.ignore import get_ignore


def test_empty():
    ignored = get_ignore([], [])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert not ignored("bar/__pycache__/file.pyc")


def test_single_regex():
    ignored = get_ignore([], [r"\.pyc$"])

    assert not ignored("amazing-file.txt")
    assert ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_regex():
    ignored = get_ignore([], [r"\.md", r"one\.rst"])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("one.md")
    assert not ignored("foo/random.txt")
    assert not ignored("bar/__pycache__/file.pyc")


def test_single_regular():
    ignored = get_ignore(["*.pyc"], [])

    assert not ignored("amazing-file.txt")
    assert ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_regular():
    ignored = get_ignore(["bar", "foo"], [])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert not ignored("one.md")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_both():
    ignored = get_ignore(["bar", "foo"], [r"\.txt", r"one\.*"])

    assert ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert ignored("one.md")
    assert ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("foo/random.txt")
    assert ignored("foo/module.pyc")
    assert ignored("bar/__pycache__/file.pyc")


def test_glob_expression():
    ignored = get_ignore(
        [
            # Glob for folder
            "**/do_ignore",
            # Glob for files
            "**/*doignore*.*",
        ],
        [],
    )
    # Root folder of our glob test files. Assume tests are run from project root.
    for ifile in glob("tests/test_ignore_glob/**/*"):
        # Convert to be relative to the tests directory since that mimics
        # the user's behavior.
        if "do_ignore" in ifile or "doignore" in ifile:
            print(f"Should ignore: {ifile})")
            assert ignored(ifile)
        else:
            print(f"Should NOT ignore: {ifile})")
            assert not ignored(ifile)
