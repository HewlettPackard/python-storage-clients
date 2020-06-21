HPE StoreOnce Gen 3 disk backup
================================================================================

API references
--------------------------------------------------------------------------------

.. autoclass:: hpestorapi.StoreOnceG3
    :members:
    :undoc-members:
    :inherited-members: timeout

Usage examples
--------------------------------------------------------------------------------

Session management
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Open Rest API session for StoreOnce Gen 4 disk backup device:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            # Perform requests to StoreOnce (get/post/put/delete)
            # ...

GET request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print StoreOnce G3 Catalyst Stores:

.. code:: python

    import xml.etree.ElementTree
    import hpestorapi

    with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            status, data = so.get('/cluster')
            if status == 200:
                tree = xml.etree.ElementTree.fromstring(data)
                name = tree.find('./cluster/properties/applianceName').text
                model = tree.find('./cluster/properties/productClass').text
                print(f'SO Name = "{name}"')
                print(f'SO Model = "{model}"')

POST request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

POST request usage. This code activate license for StoreOnce G3:

.. code:: python

    import hpestorapi

    body = {'key': 'demo', 'opcode': 'add'}

    with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
            status, data = so.post('/d2dlicenses', params=body)
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            if status == 200:
                print('Demo license activation success.')
            else:
                print('License activation failed.'
                      'Http code: %s. Response body: %s',
                      status, data)

DELETE request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code remove from Service Set 1 Catalyst Store 0:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            sset = 1
            store = 0
            status, data = so.delete(f'/cluster/servicesets/{sset}'
                                     f'/services/cat/stores/{store}')
            if status == 204:
                print('Catalyst store deleted')
            else:
                print('Can not delete catalyst store.'
                      'Http code: %s. Response: %s',
                      status, data)


PUT request
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code add NTP server to StoreOnce G3 configuration:

.. code:: python

    import hpestorapi

    with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            print('Something went wrong:')
            so.open()
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            body = {'add': 'true', 'servers': '10.0.0.2'}
            status, data = so.put('/d2dservices/clusterconf/ntp',
                                  params=body)
            if status == 200:
                print('Catalyst store deleted')
            else:
                print('Can not delete catalyst store.'
                      'Http code: %s. Response body: %s',
                      status, data)


Iterate multipage objects
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This code print all Catalyst items from all Catalyst stores:

.. code:: python

    from hpestorapi import StoreOnceG3
    from hpestorapi.storeonce3 import Iterator
    import xml.etree.ElementTree

    with StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
        try:
            so.open()
        except Exception as error:
            print('Something went wrong:')
            print(error)
        else:
            # Print table header row
            print('%15s %8s %30s %15s' % ('Store', 'ID', 'Name', 'Status'))

            # Iterate all ServiceSets
            for sset_xml in Iterator(so, '/cluster/servicesets',
                                     './servicesets/serviceset'):
                sset = xml.etree.ElementTree.fromstring(sset_xml)
                ssid = sset.find('./properties/ssid').text

                # Iterate all catalyst Stores
                store_url = (f'/cluster/servicesets'
                             f'/{ssid}/services/cat/stores/')
                for store_xml in Iterator(so, store_url, './stores/store'):
                    store = xml.etree.ElementTree.fromstring(store_xml)
                    store_id = store.find('./properties/id').text
                    store_name = store.find('./properties/name').text

                    # Iterate all Catalyst Items
                    item_url = (f'/cluster/servicesets/{ssid}'
                                f'/services/cat/stores/{store_id}/items/')
                    for item_xml in Iterator(so, item_url, './items/item'):
                        item = xml.etree.ElementTree.fromstring(item_xml)
                        item_id = item.find('./properties/id').text
                        item_name = item.find('./properties/name').text
                        item_status = item.find('./properties/status').text

                        print('%15s %8s %30s %15s' % (store_name, item_id,
                                                      item_name, item_status))
