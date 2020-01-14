hpestorapi - storage scripting for humans
************************************************************************


Package description
========================================================================

hpestorapi - python library that provides very simple way to use Rest
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
hpestorapi library depends on:

* Python 3.6 or newer
* Python `requests library <http://python-requests.org>`_

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

Usage example
========================================================================

::

  from hpestorapi import StoreServ

  with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
    array.open():
    status, data = array.get('system')
    if status == 200:
      print(f'Name={data["name"]}, SerialNumber={data["serialNumber"]}, Address={data["IPv4Addr"]}

Documentation
========================================================================
The latest version of the documentation can be found here: `pdf <https://github.com/HewlettPackard/python-storage-clients/raw/master/doc/build/latex/hpestorapi-0.9.6.pdf>`_

Unit Tests
========================================================================
You should install docker prior to running tests. To run all unit tests:
::

    # pip install -r requirements/development.txt
    # docker build -t storeserv test/storeserv
    # docker build -t storeonce3 test/storeonce3
    # tox

How to contribute
========================================================================

* Fork the repository on Github
* Create a named feature branch
* Write your change
* Write tests for your change (if applicable)
* Run the tests, ensuring they all pass
* Submit a Pull Request using Github


License
========================================================================
This project is licensed under the Apache 2.0 license.
