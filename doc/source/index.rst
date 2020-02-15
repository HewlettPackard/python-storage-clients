hpestorapi - storage scripting for humans
************************************************************************

Package description
====================================
hpestorapi - python library that provides very simple way to use Rest
API services for HPE storage and disk backup devices. Current version
supports:

* HPE 3PAR StoreServ disk arrays
* HPE Primera disk arrays
* HPE XP7 and P9500 (Command View AE Configuration manager is required)
* HPE StoreOnce Gen 3 disk backup device
* HPE StoreOnce Gen 4 disk backup device


.. toctree::
   :maxdepth: 4
   :caption: Contents:

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
    

HPE 3PAR StoreServ disk array
====================================

API reference
-------------------------------------
.. autoclass:: hpestorapi.StoreServ
    :members:
    :undoc-members:

Usage
------------------------------------

Session management
++++++++++++++++++++++++++++++++++++

Simple way to open Rest API session for StoreServ 3PAR arrays (with
exception handling and session auto-closing):

.. highlight:: py

:: 

  from hpestorapi import StoreServ

  with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
    try:
      array.open()
      # Perform requests to array (get/post/put/delete)
      # ...
    except Exception as error:
      print (error)
    else:
      # Analyze array response
      # ...

GET request
++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print some storage system information
(name, serial number and ip address):

.. highlight:: py

:: 

  from hpestorapi import StoreServ

  with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
    try:
      array.open()
      status, data = array.get('system')
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        print('Name=%s; SerialNumber=%s; Address=%s' % (
              data['name'],
              data['serialNumber'],
              data['IPv4Addr'])
             )
   
GET request can also contain filter parameter (query='...'). Filter
specifications are described in "HPE 3PAR Web Services API Developer's
Guide" (see section "WSAPI query syntax"). This code print Remote Copy
Groups names beggining with "dfs".

.. highlight:: py

:: 
    
  from hpestorapi import StoreServ

  with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
    try:
      array.open()
      status, data = array.get('remotecopygroups',
                               query='name LIKE <dfs*>')
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        for rc_group in data['members']:
          print ('RC group name = ', rc_group['name'])

POST request
++++++++++++++++++++++++++++++++++++

This code will create new host on the 3PAR array:

.. highlight:: py

:: 

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
      print ('Something went wrong:')
      raise error
    else:
      if status == 201:
        print ('Success')
      else:
        print ('Failed! Device response: ', data)

DELETE request
++++++++++++++++++++++++++++++++++++

This code will delete host from 3PAR array:

.. highlight:: py

::

  from hpestorapi import StoreServ

  with StoreServ('10.0.0.1', '3paruser', '3parpass') as array:
    hostname = 'restapi-test'
    try:
      array.open()
      status, data = array.delete(f'hosts/{hostname}')
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        print ('Success')
      else:
        print ('Fail! StoreServ 3PAR response: ', data)


PUT request
++++++++++++++++++++++++++++++++++++

This code will modify host on 3PAR array (change host persona and
location description):

.. highlight:: py

::

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
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        print ('Success')
      else:
        print ('Fail! Device response: ', data)

Exception handling
++++++++++++++++++++++++++++++++++++
Almost all methods, that perform interaction with StoreServ 3PAR
array can generate exceptions. The best practice is to handle
these exceptions.

List of method, that can raise exceptions:

* :meth:`StoreServ.open`
* :meth:`StoreServ.get`
* :meth:`StoreServ.post`
* :meth:`StoreServ.delete`
* :meth:`StoreServ.put`

.. note:: StoreServ class object constructor does not perform
    any requests to array, therefore StoreServ object initilization
    can't raise exceptions.

Exception handling example:

.. highlight:: py

::

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
      print (error)
    else:
      # We are succefully received response from array. You can
      # safely analyze array response (status and data variables)
      # ...

HPE Primera disk array
====================================
HPE Primera has minimal WSAPI changes compared to HPE 3PAR. To use
Primera WSAPI you should use class :class:`hpestorapi.Primera` with
an interface similar to class:`hpestorapi.StoreServ`


HPE XP7 and P9500 disk array
====================================

API reference
-------------------------------------
.. autoclass:: hpestorapi.Xp
    :members:
    :undoc-members:
    :inherited-members: http_timeout

Usage
------------------------------------

Session management
++++++++++++++++++++++++++++++++++++

Open Rest API session for XP array:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                  'arrayuser', 'arraypassword') as array:
    try:
      array.open()
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      # Perform requests to array (get/post/put/delete)
      # ...

GET request
++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print pool list from HPE XP array:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                  'arrayuser', 'arraypassword') as array:
    try:
      array.open()
      status, body = array.get('pools')
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
      for pool in body['data']:
        print ('ID=%s Name=%s Type=%s' % (pool['poolId'],
                                          pool['poolName'],
                                          pool['poolType'])
              )


POST request
++++++++++++++++++++++++++++++++++++

This code will create new ldev on the XP array:

.. highlight:: py

::

  import hpestorapi

  newvol = {'poolId': 1, 'byteFormatCapacity': '1G'}

  with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                  'arrayuser', 'arraypassword') as array:
    try:
      array.open()
      status, body = array.post('ldevs', json=newvol)
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        print("Success")
      else:
        print("Cannot create ldev")

DELETE request
++++++++++++++++++++++++++++++++++++

This code will delete ldev 62:

.. highlight:: py

::

    import hpestorapi

    array = hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                       'arrayuser', 'arraypassword')
    if array.open():
      ldevid = 62


PUT request
++++++++++++++++++++++++++++++++++++

This code will change label for ldev 62:

.. highlight:: py

::

  import hpestorapi

  ldevid = 62
  settings = {'label': 'RestAPI_Test'}

  with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                  'arrayuser', 'arraypassword') as array:
    try:
      array.open()
      status,body = array.put(f'ldevs/{ldevid}', json=settings)
    except Exception as error:
      print ('Something went wrong:')
      raise error
    else:
      if status == 200:
        print("Success")
      else:
        print("Cannot create ldev")


Exception handling
++++++++++++++++++++++++++++++++++++

.. highlight:: py

::

  import requests
  import hpestorapi
  with hpestorapi.Xp('cvae.domain.com', 'svp.domain.com', '123456',
                  'arrayuser', 'arraypassword') as array:
    try:
      array.open()
    except requests.exceptions.SSLError as error:
      print ('Cannot connect to Configuration Manager. SSL cert '
             'cheking is enabled, but Rest API server has no '
             'valid SSL certificate.')
    except requests.exceptions.ReadTimeout:
      timeout = array.http_timeout
      print ('Read timeout occured. The Rest server did not '
             'send any data in the allotted amount of time ',
             timeout)
    except requests.exceptions.ConnectTimeout as error:
      print ('Connection timeout occured. The request timed out '
             'while trying to connect to the Rest server.')
    except hpestorapi.Xp.AuthError as error:
      print ('Wrong username or password for the HPE XP array')
    except Exception as error:
      print (error)
    else:
      # Perform requests to array (get/post/put/delete)
      # ...


HPE StoreOnce Gen 3 disk backup
=====================================

API references
-------------------------------------

.. autoclass:: hpestorapi.StoreOnceG3
    :members:
    :undoc-members:

Usage
-------------------------------------

Session management
++++++++++++++++++++++++++++++++++++

Open Rest API session for StoreOnce Gen 4 disk backup device:

.. highlight:: py

::
    
  import hpestorapi

  with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      # Perform requests to StoreOnce (get/post/put/delete)
      # ...


GET request
++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print StoreOnce G3 Catalyst Stores:

.. highlight:: py

::

  import xml.etree.ElementTree
  import hpestorapi

  with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      status, data = so.get('/cluster')
      if status == 200:
        tree = xml.etree.ElementTree.fromstring(data)
        name = tree.find('./cluster/properties/applianceName').text
        model = tree.find('./cluster/properties/productClass').text
        print (f'SO Name = "{name}"')
        print (f'SO Model = "{model}"')

POST request
++++++++++++++++++++++++++++++++++++

POST request usage. This code activate license for StoreOnce G3:

.. highlight:: py

::

  import hpestorapi

  body = {'key': 'demo', 'opcode': 'add'}

  with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
      status, data = so.post('/d2dlicenses', params=body)
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      if status == 200:
        print('Demo license activation success.')
      else:
        print('License activation failed.'
              'Http code: %s. Response body: %s',
              status, data)


DELETE request
++++++++++++++++++++++++++++++++++++

This code remove from Service Set 1 Catalyst Store 0:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
    except Exception as error:
      print ('Something went wrong:')
      print (error)
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
++++++++++++++++++++++++++++++++++++

This code add NTP server to StoreOnce G3 configuration:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      print ('Something went wrong:')
      so.open()
    except Exception as error:
      print ('Something went wrong:')
      print (error)
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
++++++++++++++++++++++++++++++++++++

This code print all Catalyst items from all Catalyst stores:

.. highlight:: py

::

  from hpestorapi import StoreOnceG3
  from hpestorapi.storeonce3 import Iterator
  import xml.etree.ElementTree

  with StoreOnceG3('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      # Print table header row
      print ('%15s %8s %30s %15s' %('Store', 'ID', 'Name', 'Status'))

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

            print ('%15s %8s %30s %15s' %(store_name, item_id,
                                          item_name, item_status))
                    

HPE StoreOnce Gen 4 disk backup
=====================================

API references
-------------------------------------

.. autoclass:: hpestorapi.StoreOnceG4
    :members:
    :undoc-members:

Usage
-------------------------------------

Session management
++++++++++++++++++++++++++++++++++++

Open Rest API session for StoreOnce Gen 4 disk backup device:

.. highlight:: py

::
    
  import hpestorapi

  with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
    try:
      print ('Something went wrong:')
      so.open()
    except Exception as error:
      print (error)
    else:
      # Perform requests to StoreOnce (get/post/put/delete)
      # ...
        
        
GET request
++++++++++++++++++++++++++++++++++++

Simple GET request usage. This code print StoreOnce G4 groups:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
    try:
      so.open()
      status, data = so.get('/rest/groups')
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      if status == 200:
        for group in data['members']:
            print (group['groupName'])


POST request
++++++++++++++++++++++++++++++++++++

This code will create new Catalyst client:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
    new_client = {'name': 'sqlserver',
                  'description': "New host',
                  'password': "secretpass'
                 }
    try:
      so.open()
      status, data = so.post('/api/v1/data-services/cat/clients',
                             json=new_client)
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      if status == 201:
        print ('Host succefully added.')
      else:
        print ('Fail! Cannot add new catalyst client. Details:',
               data)
                
DELETE request
++++++++++++++++++++++++++++++++++++

This code remove CIFS share:

.. highlight:: py

::

  import hpestorapi

  with hpestorapi.StoreOnceG4('10.0.0.1', 'Admin', 'password') as so:
    share = 'CifsShare01'
    try:
      so.open()
      status, _ = so.delete('/api/v1/data-services/nas/shares'
                            '/share/{id}'.format(id=share))
    except Exception as error:
      print ('Something went wrong:')
      print (error)
    else:
      if status == 204:
        print ('Share succefully removed.')
      elif status == 404:
        print ('Fail! Share does not exist.')
      else:
        print ('Fail! Cannot remove share.')

PUT request
++++++++++++++++++++++++++++++++++++

This code will update current SMTP configuration:

.. highlight:: py

::
    
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
      print ('Something went wrong:')
      print (error)
    else:
      print ('SMTP configuration succefully updated.')
    

Debug
=====================================

Enable logging
-------------------------------------
hpestorapi uses Python’s Standard Library `logging module
<https://docs.python.org/3/library/logging.html>`_. Simple python script
with enabled debug logging:

.. highlight:: py

::

  #!/usr/bin/env python3
  # -*- coding: utf-8 -*-

  import logging
  import hpestorapi

  if __name__ == '__main__':
    # Setup logging format, level, logfile
    logfmt = ('[%(asctime)s] '
              '%(levelname)-8s '
              '%(filename)-12s:%(lineno)-3d '
              '%(message)s')

    logging.basicConfig(format=logfmt,
                        level=logging.WARNING,
                        filename='messages.log')

    # Set XP, 3PAR, StoreOnce loglevel
    logging.getLogger("hpestorapi.xp").setLevel(logging.DEBUG)
    logging.getLogger("hpestorapi.storeserv").setLevel(logging.DEBUG)
    logging.getLogger("hpestorapi.storeonce").setLevel(logging.DEBUG)

    """
    Your code starts here
    """

Five logging levels are used:

* DEBUG
* INFO
* WARNING
* ERROR
* FATAL

Bug reports
-------------------------------------
If you have found a bug, please create an `issue in GitHub <https://github.com/HewlettPackard/python-storage-clients/issues>`_.
And do not hesitate to contact me: Ivan Smirnov <ivan.smirnov@hpe.com>

