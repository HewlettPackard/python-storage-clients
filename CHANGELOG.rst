Change Log
================================================================================

Version 1.0.0 (Jan 18, 2021)
--------------------------------------------------------------------------------

* API fixation
* Internal design improvements
* Documentation improvements


Version 0.9.12 (August 12, 2020)
========================================================================
Enhancement:

* Package version number added as __version__ attribute (PEP 396).

Version 0.9.11 (July 03, 2020)
========================================================================
Issue resolved:

* Fix: unrequested logging to stderr removed

Version 0.9.9 (May 15, 202)
--------------------------------------------------------------------------------
Issue resolved:

* StoreOnceG3: Standart HTTP headers (Accept, Content-Type) can be overrided by user (GitHub issue #6).

Version 0.9.8 (April 22, 2020)
--------------------------------------------------------------------------------

* Minor changes in StoreOnceG3 implementation
* Documentation coverage improvments

There is no plans to implement new functions in branch 0.9.x. Only for bugfixes.


Version 0.9.7 (March 7, 2020)
--------------------------------------------------------------------------------
Internal improvements:

* API interface fixation.

Bug fixed:

* 3PAR and Primera filter query string encoding bug.
* Parameter verify added to 3PAR and Primera for self signed SSL certs support.

Version 0.9.6 (Jan 20, 2020)
--------------------------------------------------------------------------------
General improvements:

* HPE Primera disk arrays support

Version 0.9.5 (Dec 15, 2019)
--------------------------------------------------------------------------------
General improvements:

* Package is ready for upload to Python Package Index (pypi)

Unit tests improvements:

* Migrated to pytest and tox environments
* Migrated HPE 3PAR tests to flask app in docker container (works like an 3PAR array WSAPI emulator)


Version 0.9.4 (Nov 20, 2019)
--------------------------------------------------------------------------------
Initial Public Release. Supported devices:

* HPE 3PAR StoreServ arrays
* HPE XP7 and P9500 (Command View AE Configuration manager is required)
* HPE StoreOnce G3 disk backup device
* HPE StoreOnce G4 disk backup device