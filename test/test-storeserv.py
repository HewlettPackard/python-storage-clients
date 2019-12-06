#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   (C) Copyright 2017-2019 Hewlett Packard Enterprise Development LP
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

"""
.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

import unittest
import requests
#import multiprocessing
import hpestorapi
from storeserv.restserver import ApiInstance
from time import sleep

class TestStoreServ(unittest.TestCase):
    def worker(self):
        server = ApiInstance()
        server.run()

    def setUp(self):
#        self.process = multiprocessing.Process(target=self.worker)
#        self.process.start()
        sleep(3)

    def tearDown(self):
        self.process.terminate()
        self.process.join()
        #while self.process.is_alive():
        #    sleep(1)

    def test_exception_connection_error(self):
        """
        ConnectionError exception raising test.
        Wrong network address, firewall or rest api connection limit ...
        """
        array = hpestorapi.StoreServ('fake-address', '3paradm', '3pardata', ssl=False)
        with self.assertRaises(requests.exceptions.ConnectionError):
            array.open()


    def test_exception_auth_error(self):
        """
        AuthError exception raising text.
        Wrong user or password.
        """
        array = hpestorapi.StoreServ('127.0.0.1', 'user', 'wrong-password', ssl=False)
        with self.assertRaises(hpestorapi.storeserv.AuthError):
            array.open()

    '''
    def test_get(self):
        """
        GET request
        """
        array = hpestorapi.StoreServ('127.0.0.1', '3paradm', '3pardata', ssl=False)
        array.open()
        status, _ = array.get('system')
        self.assertEqual(status, 200)
        
    #@unittest.skipUnless(user == '3paradm', 'Need 3PAR admin rights')
    def test_post(self):
        """
        POST request
        """
        array = hpestorapi.StoreServ('127.0.0.1', 'user', 'password', ssl=False)
        array.open()
        status, _ = array.post('hosts', {'name': 'RestApiTestHost',
                                         'persona': 5})
        self.assertEqual(status, 201)
    '''

if __name__ == '__main__':
    unittest.main()
