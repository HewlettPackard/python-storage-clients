.. image:: https://travis-ci.org/HewlettPackard/python-storage-clients.svg?branch=latest
    :target: https://travis-ci.org/HewlettPackard/python-storage-clients

.. image:: https://readthedocs.org/projects/hpestorapi/badge/?version=latest
    :target: https://hpestorapi.readthedocs.io/en/latest/?badge=latest

.. image:: https://badges.gitter.im/python-storage-clients/community.svg
    :target: https://gitter.im/python-storage-clients/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge

hpestorapi
************************************************************************


Package description
========================================================================

hpestorapi is a python library that allows a simple way to use Rest
API services for HPE storage and disk backup devices. Current version
supports:

* HPE 3PAR StoreServ disk arrays
* HPE Primera disk arrays
* HPE XP7 and P9500 (Command View AE Configuration manager is required)
* HPE StoreOnce G3 disk backup device
* HPE StoreOnce G4 disk backup device

Installation
========================================================================

Requirements
--------------------------------------------------------------------------
hpestorapi library requires:

* CPython 3.6+ or PyPy3 interpreter
* Python `requests library <http://python-requests.org>`_

Installation from PyPI
--------------------------------------------------------------------------
To download and install hpestorapi you can use pip:
::

    # pip install hpestorapi

Installation from GitHub
--------------------------------------------------------------------------
Get a copy of source code
::

    # git clone https://github.com/HewlettPackard/python-storage-clients.git
    # cd python-storage-clients

Install the package with dependencies:
::

    # python setup.py install

Import hpestorapi library to your python script:

.. code:: python

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-

    import hpestorapi

Usage example
========================================================================

.. code:: python

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        array.open()
        status, data = array.get('system')
        if status == 200:
            print('Name=%s' % data["name"],
                  'SerialNumber=%s' % data["serialNumber"],
                  'Address=%s' % data["IPv4Addr"]
                  )

Documentation
========================================================================
The latest version of the documentation can be found here:
`html <https://hpestorapi.readthedocs.io/en/latest/?badge=latest>`_

Issues
========================================================================
If you encounter any problems, please `open an issue <https://github
.com/HewlettPackard/python-storage-clients/issues>`_ along with a detailed
description. Your questions are welcomed in `gitter chat <https://gitter
.im/python-storage-clients>`_.

Package Version Numbers
========================================================================
This project follows `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


Unit Tests
========================================================================
You should install docker prior to running tests. To run all unit tests:
::

    # pip install -r requirements/development.txt
    # docker build -t storeserv test/storeserv
    # docker build -t storeonce3 test/storeonce3
    # tox



