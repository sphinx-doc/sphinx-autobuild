# Contributing

Thank you for being interested in contributing to the `sphinx-autobuild`! You
are awesome. :sparkles:

See the [EBP Contributing Guide](https://executablebooks.org/en/latest/contributing.html) for general details,
then this page contains information to help you get started with development on this project.

## Feature Suggestions

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project. :)

## Development

### Set-up

1. Fork the `sphinx-autobuild` repo on GitHub.
2. Clone your fork locally.

    ```
    $  git clone git@github.com:your_name_here/sphinx-autobuild.git
    ```

To work on this project, you need Python 3.6 or newer. Most of this project's
development workflow commands use [`nox`](https://nox.readthedocs.io/).

If you're not sure how to install nox, it is recommended to set it up in an isolated environment with [`pipx`](https://pipxproject.github.io/pipx/installation/):

```bash
pip install pipx
pipx ensurepath
pipx install nox
```

### Running Tests

This project has a test suite to ensure that things work properly. The tests can be run using:

```bash
nox -s tests
```

This will run tests against all supported version of Python that are installed.

If you want to run tests for a specific version of Python (say, 3.8), you can
do so using:

```bash
nox -s tests-3.8
```

### Running Linters

The code style in this project is enforced with multiple automated linters. You
can run them using:

```bash
nox -s lint
```

### Running this project

You can test your local copy of this project, by building this project's docs/ directory with it.

```bash
nox -s docs-live
```

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request has code, it should include tests.
2. If the pull request adds functionality, the docs should be updated.
3. Make sure that the tests pass for all supported Python versions (see the
   Travis builds for details).

## Release Process

* Update the `NEWS.rst` file (replace the unreleased title with the current
  date).
* Bump the version in the `src/sphinx_autobuild/__init__.py` file.
* Update the AUTHORS file (`git shortlog -s -e -n | cut -f 2- > AUTHORS` on *nix).
* Push everything and make sure the Travis tests still pass.
* Run `flit publish` to build the package and release it on PyPI.
* Add a new unreleased section to the top of the `NEWS.rst` file.
