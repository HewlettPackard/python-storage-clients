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
    Returns StoreOnce network port number
    """
    return os.environ.get('STOREONCE3_443_TCP', '443')

def test_exception_connection_error(port):
    """
    ConnectionError exception raising test.
    Wrong network address, firewall or rest api connection limit ...
    """
    so = hpestorapi.StoreOnceG3('wrong-address', 'user', 'password')
    with pytest.raises(requests.exceptions.ConnectionError):
        so.open()


if __name__ == '__main__':
    pass
