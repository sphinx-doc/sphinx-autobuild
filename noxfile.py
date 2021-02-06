"""Development automation."""

import nox


def _install_this_editable(session, *, extras=None):
    if extras is None:
        extras = []

    session.install("flit")
    session.run(
        "flit",
        "install",
        "-s",
        "--deps=production",
        "--extras",
        ",".join(extras),
        silent=True,
    )


@nox.session(reuse_venv=True)
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.6", "3.7", "3.8"])
def test(session):
    _install_this_editable(session, extras=["test"])

    default_args = ["--cov-report", "term", "--cov", "sphinx_autobuild"]
    args = session.posargs or default_args

    session.run("pytest", *args)


@nox.session(reuse_venv=True)
def docs(session):
    _install_this_editable(session, extras=["docs"])
    session.run("sphinx-build", "-b", "html", "docs/", "build/docs")


@nox.session(name="docs-live", reuse_venv=True)
def docs_live(session):
    _install_this_editable(session, extras=["docs"])
    session.run(
        "sphinx-autobuild", "-b", "html", "docs/", "build/docs", *session.posargs
    )
