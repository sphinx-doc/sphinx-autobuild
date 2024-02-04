from sphinx_autobuild.ignore import Ignore


def test_empty():
    ignored = Ignore([], [])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert not ignored("bar/__pycache__/file.pyc")


def test_single_regex():
    ignored = Ignore([], [r"\.pyc$"])

    assert not ignored("amazing-file.txt")
    assert ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_regex():
    ignored = Ignore([], [r"\.md", r"one\.rst"])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("one.md")
    assert not ignored("foo/random.txt")
    assert not ignored("bar/__pycache__/file.pyc")


def test_single_regular():
    ignored = Ignore(["*.pyc"], [])

    assert not ignored("amazing-file.txt")
    assert ignored("module.pyc")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert not ignored("one.md")
    assert not ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_regular():
    ignored = Ignore(["bar", "foo"], [])

    assert not ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert not ignored("one.md")
    assert not ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("foo/random.txt")
    assert ignored("bar/__pycache__/file.pyc")


def test_multiple_both():
    ignored = Ignore(["bar", "foo"], [r"\.txt", r"one\.*"])

    assert ignored("amazing-file.txt")
    assert not ignored("module.pyc")
    assert ignored("one.md")
    assert ignored("one.rst")
    assert not ignored("two.rst")
    assert ignored("foo/random.txt")
    assert ignored("foo/module.pyc")
    assert ignored("bar/__pycache__/file.pyc")
