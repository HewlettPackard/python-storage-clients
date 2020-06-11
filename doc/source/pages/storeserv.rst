HPE 3PAR StoreServ disk array
================================================================================

API reference
--------------------------------------------------------------------------------
.. autoclass:: hpestorapi.StoreServ
    :members:
    :undoc-members:

Usage examples
--------------------------------------------------------------------------------

Session management
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

A simple way to open a Rest API session for StoreServ 3PAR arrays (with
exception handling and session auto-closing):

.. code:: python

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            # Perform requests to array (get/post/put/delete)
            # ...
        except Exception as error:
            print(error)
        else:
            # Analyze array response
            # ...

GET request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Simple GET request usage. This following code prints storage system
information (name, serial number and IP address):

.. code:: python

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            status, data = array.get('system')
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Name=%s; ' % data['name'],
                      'SerialNumber=%s; ' % data['serialNumber'],
                      'Address=%s' % data['IPv4Addr']
                      )

GET request can also contain filter parameter (query='...'). Filter
specifications are described in "HPE 3PAR Web Services API Developer's
Guide" (see section "WSAPI query syntax"). The following code prints Remote
Copy Groups names beginning with "dfs".

.. code:: python

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            status, data = array.get('remotecopygroups', query='name LIKE <dfs*>')
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                for rc_group in data['members']:
                    print('RC group name = ', rc_group['name'])

POST request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The following code creates a new host on the 3PAR array:

.. code:: python

    from hpestorapi import StoreServ

    newhost = {
        'name': 'restapi-test',
        'persona': 2,
        'FCWWNs': ['50:01:55:55:55:55:55:55',
                   '50:01:66:66:66:66:66:66']
    }

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            status, data = array.post('hosts', newhost)
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 201:
                print('Success')
            else:
                print('Failed! Device response: ', data)


DELETE request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The following code deletes a host from the 3PAR array:

.. code:: python

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        hostname = 'restapi-test'
        try:
            array.open()
            status, data = array.delete(f'hosts/{hostname}')
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Success')
            else:
                print('Fail! StoreServ 3PAR response: ', data)


PUT request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The following code modifies a host on the 3PAR array (change host persona and
location description):

.. code:: python

    from hpestorapi import StoreServ

    hostname = 'restapi-test'
    modify = {
        'persona': 1,
        'descriptors': {'location': 'Rack 2/42, Unit 34'}
    }

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            status, data = array.put(f'hosts/{hostname}', body=modify)
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Success')
            else:
                print('Fail! Device response: ', data)


Exception handling
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Almost all methods that perform interaction with the HPE StoreServ 3PAR
array can generate exceptions. The best practice is to handle
these exceptions.

List of method that can raise exceptions:

* :meth:`StoreServ.open`
* :meth:`StoreServ.get`
* :meth:`StoreServ.post`
* :meth:`StoreServ.delete`
* :meth:`StoreServ.put`

.. note:: StoreServ class object constructor does not perform
    any requests to array, therefore StoreServ object initilization
    can't raise exceptions.

Exception handling example:

.. code:: python

    import requests

    from hpestorapi import StoreServ

    with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
        try:
            array.open()
            status, data = array.get('system')
        except requests.exceptions.SSLError as error:
            print('SSL error occured. Please check SSL connection '
                  'options.')
        except requests.exceptions.ReadTimeout:
            print('Read timeout occured. The StoreServ 3PAR array did '
                  'not send any data in the alloted amount of time.')
        except requests.exceptions.ConnectTimeout as error:
            print('Connection timeout occured. The request timed out '
                  'while trying to connect to the StoreServ 3PAR '
                  'array.')
        except hpestorapi.storeserv.AuthError as error:
            print('Wrong user name or password for the StoreServ 3PAR '
                  'array.')
        except Exception as error:
            print(error)
        else:
            # We are successfully received response from array. You can
            # safely analyze array response (status and data variables)
            # ...
