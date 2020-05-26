HPE StoreOnce Gen 4 disk backup
================================================================================

API references
--------------------------------------------------------------------------------

.. autoclass:: hpestorapi.StoreOnceG4
    :members:
    :undoc-members:

Usage examples
--------------------------------------------------------------------------------

Session management
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Open Rest API session for StoreOnce Gen 4 disk backup device:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
        try:
            print('Something went wrong:')
            so.open()
        except Exception as error:
            print(error)
        else:
            # Perform requests to StoreOnce (get/post/put/delete)
            # ...


GET request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print StoreOnce G4 groups:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
            status, data = so.get('/rest/groups')
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            if status == 200:
                for group in data['members']:
                    print(group['groupName'])


POST request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code will create new Catalyst client:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
        new_client = {'name': 'sqlserver', 'description': 'New host',
                      'password': 'secretpass'
        }
        try:
            so.open()
            status, data = so.post('/api/v1/data-services/cat/clients',
                                   json=new_client)
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            if status == 201:
                print('Host succefully added.')
            else:
                print('Fail! Cannot add new catalyst client. Details:', data)

DELETE request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code remove CIFS share:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
        share = 'CifsShare01'
        try:
            so.open()
            status, _ = so.delete('/api/v1/data-services/nas/shares'
                                  '/share/{id}'.format(id=share))
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            if status == 204:
                print('Share succefully removed.')
            elif status == 404:
                print('Fail! Share does not exist.')
            else:
                print('Fail! Cannot remove share.')

PUT request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code will update current SMTP configuration:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
        body = {'emailConfigurations': {
            'smtpPort': 25,
            'enabled': 'true',
            'senderEmailAddress': 'sender@company.com',
            'password': 'secretpassword',
            'smtpServer': 'email.company.com'
        }
        }
        try:
            so.open()
            status, data = so.put('/rest/email', json=body)
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            print('SMTP configuration succefully updated.')
