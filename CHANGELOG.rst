Change Log
************************************************************************

Version 0.9.4 (Nov 20, 2019)
========================================================================
Initial Public Release. Supported devices:

* HPE 3PAR StoreServ arrays
* HPE XP7 and P9500 (Command View AE Configuration manager is required)
* HPE StoreOnce G3 disk backup device
* HPE StoreOnce G4 disk backup device

Version 0.9.5 (Dec 15, 2019)
========================================================================
General improvements:

* Package is ready for upload to Python Package Index (pypi)
* HPE Primera disk arrays support

Unit tests improvements:

* Migrated to pytest and tox environments
* Migrated HPE 3PAR tests to flask app in docker container (works like an 3PAR array WSAPI emulator)