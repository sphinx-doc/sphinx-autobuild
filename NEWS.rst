Changelog
=========

unreleased
----------

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

* Added ``-r``, ``--re-ignore`` command line argumet to exclude paths using
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
