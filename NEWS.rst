Changelog
=========

unreleased
----------

2024.09.17 - 2024-09-17
-----------------------

* Relax checks for paths that aren't required to exist.

2024.09.03 - 2024-09-03
-----------------------

* Fix support for Python 3.9.
* Fix running ``sphinx-autobuild`` via entry point scripts.
* Run ``sphinx-build`` in a subprocess to mitigate autdoc issues.
* Support the ``-M`` 'make mode' option for ``sphinx-build``.

2024.04.16 - 2024-04-16
-----------------------

* Add a missing dependency on ``watchfiles``.
* Adopt Ruff in place of flake8 and black.

2024.04.13 - 2024-04-13
-----------------------

* Drop ``python-livereload``.
* Add ``starlette`` and ``uvicorn`` as dependencies.
* Implement hot reloading via websockets.
* Run Sphinx rebuilds in an asynchronous executor.

2024.02.04 - 2024-02-04
-----------------------

* Declare support for Python 3.9, 3.10, 3.11, and 3.12
* Drop support for Python 3.8 and earlier
* Allow passing relative paths to ``--ignore``
* Support all valid ``sphinx-build`` options (except Make-mode)
* Fix path issues on Windows
* Differentiate pre-build command failures from Sphinx failures

2021.03.14 - 2021-03-14
-----------------------

* Change output handling for subprocesses.
* Present helpful error message when the subprocesses fail.
* Skip the main sphinx build, if pre-build commands fail.

2020.09.01 - 2020-09-01
-----------------------

* Adopt Calendar Versioning.
* Modernize codebase and require Python 3.6+.
* Directly depend on ``sphinx``.
* Rewritten documentation.
* Invoke sphinx via ``{sys.executable} -m sphinx`` instead of ``sphinx-build``.
* Trim dependencies down to only ``livereload`` and ``sphinx``.
* Drop custom adapter for ``watchdog``.
* Drop ``--poll`` flag.
* Drop single letter variants for flags that were specific to sphinx-autobuild.

0.7.1 - 2017/07/05
------------------

* Remove spurious virtualenv directory from published packages.


0.7.0 - 2017/07/05
------------------

* Add support for python 3.5, 3.6 and deprecate official python 2.6 support.
* Add ``__main__`` module for python 3.
* Add a ``--version`` argument.


0.6.0 – 2016/02/14
------------------

* Support ``-p 0``, ``--port=0`` to automatically chose an available port.
* Added ``-B``, ``--open-browser`` to automatically open the documentation upon
  build.
* Added Kate swap files to the list of files ignored by default
* Automatically build docs on startup (can be disabled with ``--no-initial``).
* Added ``--poll`` to force polling the FS for changes (useful for
  networked/virtualized mountpoints).
* Compatibility with livereload >= 2.4.1.


0.5.2 – 2015/04/10
------------------

* Added ``-r``, ``--re-ignore`` command line argument to exclude paths using
  regexes.


0.5.0 – 2015/01/28
------------------

* Added ``-z``, ``--watch`` command line argument to watch arbitrary folders.


0.4.0 – 2014/12/23
------------------
* Added ``-i``, ``--ignore`` command line argument to ignore files by the glob
  expression.
* Added basic tests for the entry point script.
* PEP 257 improvements.
* Automated tests on travis integration and coverage reporting.
* Compatibility with livereload >= 2.3.0.
* Compatibility with Python 2.6 and 2.7.
* Provisional compatibility with Python 3.3 and 3.4.


0.3.0 – 2014/08/21
------------------


0.2.3 – 2013/12/25
------------------
* Ignore the paths indicated by the ``-w`` and ``-d`` arguments when watching
  for changes to the documentation.


0.2.1 – 2013/12/25
------------------
* Catch subprocess PTY reading errors.


0.2.0 – 2013/12/25
------------------
* Explicitly parse sphinx-build arguments for better compatibility.


0.1.0 – 2013/12/25
------------------
* Initial release.
