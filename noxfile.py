"""Development automation."""

import nox


@nox.session(reuse_venv=True)
def lint(session):
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session):
    session.install("-e", ".[test]", silent=True)
    session.run("pytest", *session.posargs)


@nox.session(reuse_venv=True)
def docs(session):
    session.install("-e", ".", silent=True)
    session.run("sphinx-build", "-b", "html", "docs/", "build/docs")


@nox.session(name="docs-live", reuse_venv=True)
def docs_live(session):
    session.install("-e", ".", silent=True)
    session.run(
        "sphinx-autobuild", "-b", "html", "docs/", "build/docs", *session.posargs
    )
