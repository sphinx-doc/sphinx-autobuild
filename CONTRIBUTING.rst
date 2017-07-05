============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/GaretJax/sphinx-autobuild/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to
whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "Feature
request" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Sphinx Documentation Automatic Builder could always use more documentation, whether as
part of the official Sphinx Documentation Automatic Builder docs, or even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/GaretJax/sphinx-autobuild/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions are
  welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `sphinx-autobuild` for
local development.

1. Fork the `sphinx-autobuild` repo on GitHub.

2. Clone your fork locally::

    $  git clone git@github.com:your_name_here/sphinx-autobuild.git

3. Install your local copy into a virtualenv. Assuming you have
   virtualenvwrapper installed, this is how you set up your fork for local
   development::

    $  mkvirtualenv sphinx-autobuild
    $  cd sphinx-autobuild/
    $  pip install -e . -r requirements-dev.txt

4. Create a branch for local development::

    $  git checkout -b name-of-your-bugfix-or-feature

5. Now you can make your changes locally.

6. When you're done making changes, check that your changes pass all tests::

    $  fab lint
    $  py.test

7. Commit your changes and push your branch to GitHub::

    $  git add .
    $  git commit -m "Your detailed description of your changes."
    $  git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request has code, it should include tests.
2. If the pull request adds functionality, the docs should be updated.
3. Make sure that the tests pass for all supported Python versions (see the
   Travis builds for details).

Tips
----

To run a subset of tests::

  $  py.test sphinx_autobuild/test/tests_file.py

Authoring a release
-------------------

* Update the ``NEWS.rst`` file (replace the unreleased title with the current
  date).
* Bump ther version in the ``sphinx_autobuild/__init__.py`` file.
* Update the AUTHORS file by running ``fab authors``.
* Make sure that the working tree is clean (either commit or stash the changes).
* Make sure that ``check-manifest`` is happy.
* Push everything and make sure the Travis tests still pass.
* Run ``fab release`` to build the package and release it on PyPI.
* Add a new unreleased section to the top of the ``NEWS.rst`` file.
