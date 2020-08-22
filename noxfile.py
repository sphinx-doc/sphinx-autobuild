"""Development automation."""

import nox


@nox.session
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.6", "3.7", "3.8"])
def test(session):
    session.install(".[test]")

    default_args = ["--cov-report", "term", "--cov", "sphinx_autobuild"]
    args = session.posargs or default_args

    session.run("pytest", *args)


@nox.session
def docs(session):
    session.install(".[docs]")
    session.run("sphinx-build", "-b", "html", "docs/", "build/docs")
