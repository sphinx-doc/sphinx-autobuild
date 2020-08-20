"""Development automation."""

import nox


@nox.session
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.6", "3.7", "3.8"])
def test(session):
    session.install(".[test]")
    # fmt: off
    default_args = [
        "--cov-report", "term",
        "--cov", "sphinx_autobuild",
        "sphinx_autobuild",
    ]
    # fmt: on
    session.run("pytest", *(session.posargs or default_args))


@nox.session
def docs(session):
    session.install(".[docs]")
    session.run("sphinx-build", "-b", "html", "docs/", "build/docs")
