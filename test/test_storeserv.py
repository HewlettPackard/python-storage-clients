#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   (C) Copyright 2017-2020 Hewlett Packard Enterprise Development LP
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

# pylint: disable=redefined-outer-name
# ^^^ this

import os

import pytest
import requests

import hpestorapi


@pytest.fixture
def port():
    """
    Returns 3PAR WSAPI network port number
    """
    return os.environ.get('STORESERV_8008_TCP', 8008)

def test_exception_connection_error(port):
    """
    ConnectionError exception raising test.
    Wrong network address, firewall or rest api connection limit ...
    """
    array = hpestorapi.StoreServ('wrong-address', 'user', 'password', ssl=False, port=port)
    with pytest.raises(requests.exceptions.ConnectionError):
        array.open()

def test_exception_auth_error(port):
    """
    AuthError exception raising text.
    Wrong user or password.
    """
    array = hpestorapi.StoreServ('127.0.0.1', 'user', 'wrong-password', ssl=False, port=port)
    with pytest.raises(hpestorapi.storeserv.AuthError):
        array.open()

def test_get(port):
    """
    GET request
    """
    with hpestorapi.StoreServ('127.0.0.1', '3paradm', '3pardata', ssl=False, port=port) as array:
        array.open()
        status, _ = array.get('system')
        assert status == 200

def test_post(port):
    """
    POST request
    """
    with hpestorapi.StoreServ('127.0.0.1', '3paradm', '3pardata', ssl=False, port=port) as array:
        array.open()
        status, _ = array.post('hosts', {'name': 'RestApiTestHost', 'persona': 5})
        assert status == 201


if __name__ == '__main__':
    pass
