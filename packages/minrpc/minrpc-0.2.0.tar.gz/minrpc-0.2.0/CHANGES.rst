Changelog
~~~~~~~~~

(dates are in the form ``DD.MM.YYYY``)

0.2.0
=====
Date: 17.09.2025

- drop support with python < 3.4
- avoid call to os.closerange to fix starting overhead in cpymad


0.1.0
=====
Date: 28.10.2020

- fix UnpicklingError: pickle data was truncated
  see: https://github.com/hibtc/cpymad/issues/72


0.0.11
======
Date: 13.04.2019

- remove obsolete OrderedDict export
- simplifications in build/setup scripts
- remove py33 tests


0.0.10
======
Date: 18.10.2018

Pure maintenance release with continuous integration improvements:

- automatically upload release to PyPI
- add automatic style and sanity checks
- fix some style issues
- cleanup in .travis.yml


0.0.9
=====
Date: 18.10.2018

- add ``__bool__`` for ``RemoteModule`` indicating whether the connection has
  been closed
- return ``self`` from ``ChangeDirectory.__enter__``
- wait for subprocess completion in ``Client.close()``


0.0.8
=====
Date: 30.08.2018

- improve error prevention during connection shutdown


0.0.7
=====
Date: 11.06.2018

- simplify module access, backward incompatible!!
- add overridable ``Client._communicate`` method


0.0.6
=====
Date: 30.11.2017

- improve error checking before/after requests
- catch more exceptions in __del__
- provide copyright notice as unicode


0.0.5
=====
Date: 13.11.2017

- allow locking during request (for thread safety)


0.0.4
=====
Date: 12.07.2017

- remember error state of connection (whether RemoteProcessCrashed was raised)
- export an OrderedDict type that preserves insertion order


0.0.3
=====
Date: 24.09.2016

- fix raised exception type in client


0.0.2
=====
Date: 19.09.2016

- fix problem with exception handling


0.0.1
=====
Date: 19.09.2016

- copied from cpymad 0.14.3
