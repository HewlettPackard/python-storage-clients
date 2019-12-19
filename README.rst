hpestorapi - storage scripting for humans
************************************************************************


Package description
========================================================================

hpestorapi - python library that provides very simple way to use Rest
API services for HPE storage and disk backup devices. Current version
supports:

* HPE 3PAR StoreServ arrays
* HPE XP7 and P9500 (Command View AE Configuration manager is required)
* HPE StoreOnce G3 disk backup device
* HPE StoreOnce G4 disk backup device

Installation
========================================================================

Requirements
--------------------------------------------------------------------------
hpestorapi library depends on:

* Python 3.6 or newer
* Python `requests library <http://python-requests.org>`_ version 2.19.1 or newer

Install from PyPI
--------------------------------------------------------------------------
To download and install hpestorapi you can use pip:
::

    # pip install hpestorapi

Install from GitHub
--------------------------------------------------------------------------
Get a copy of source code
::

    # git clone https://github.com/HewlettPackard/python-storage-clients.git
    # cd python-storage-clients

Install package with dependencies:
::

    # python setup.py install

Import hpestorapi library in your python script:
::

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-

    import hpestorapi


Unit Tests
========================================================================
To run all unit tests:
::

    # pip install -r requirements/development.txt
    # docker build -t storeserv test/storeserv
    # docker build -t storeonce3 test/storeonce3
    # tox


Documentation
========================================================================
The latest version of the documentation can be found here: `pdf <https://github.com/HewlettPackard/python-storage-clients/raw/master/doc/build/latex/hpestorapi-0.9.6.pdf>`_

