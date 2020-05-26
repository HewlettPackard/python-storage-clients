HPE XP7 and P9500 disk array
================================================================================

API reference
--------------------------------------------------------------------------------
.. autoclass:: hpestorapi.Xp
    :members:
    :undoc-members:
    :inherited-members: http_timeout

Usage examples
--------------------------------------------------------------------------------

Session management
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Open Rest API session for XP array:

.. code:: python

    import hpestorapi

    with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword') as array:
        try:
            array.open()
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            # Perform requests to array (get/post/put/delete)
            # ...

GET request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print pool list from HPE XP array:

.. code:: python

    import hpestorapi

    with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword') as array:
        try:
            array.open()
            status, body = array.get('pools')
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                for pool in body['data']:
                    print('ID=%s ' % pool['poolId'],
                          'Name=%s ' % pool['poolName'],
                          'Type=%s' % pool['poolType']
                          )


POST request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code will create new ldev on the XP array:

.. code:: python

    import hpestorapi

    newvol = {'poolId': 1, 'byteFormatCapacity': '1G'}

    with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword') as array:
        try:
            array.open()
            status, body = array.post('ldevs', json=newvol)
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Success')
            else:
                print('Cannot create ldev')

DELETE request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code will delete ldev 62:

.. code:: python

    import hpestorapi

    ldevid=62

    array = hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                          'arrayuser', 'arraypassword') as array:
        try:
            array.open()
            status, body = array.post(f'ldevs/62')
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Success')
            else:
                print(f'Cannot delete ldev with id {ldevid}')


PUT request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code will change label for ldev 62:

.. code:: python

    import hpestorapi

    ldevid = 62
    settings = {'label': 'RestAPI_Test'}

    with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword') as array:
        try:
            array.open()
            status, body = array.put(f'ldevs/{ldevid}', json=settings)
        except Exception as error:
            print('Something went wrong:')
            raise error
        else:
            if status == 200:
                print('Success')
            else:
                print('Cannot create ldev')


Exception handling
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code:: python

    import requests
    import hpestorapi

    with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword') as array:
        try:
            array.open()
        except requests.exceptions.SSLError as error:
            print('Cannot connect to Configuration Manager. SSL cert '
                  'cheking is enabled, but Rest API server has no '
                  'valid SSL certificate.')
        except requests.exceptions.ReadTimeout:
            timeout = array.http_timeout
            print('Read timeout occured. The Rest server did not '
                  'send any data in the allotted amount of time ',
                  timeout)
        except requests.exceptions.ConnectTimeout as error:
            print('Connection timeout occured. The request timed out '
                  'while trying to connect to the Rest server.')
        except hpestorapi.Xp.AuthError as error:
            print('Wrong username or password for the HPE XP array')
        except Exception as error:
            print(error)
        else:
            # Perform requests to array (get/post/put/delete)
            # ...
