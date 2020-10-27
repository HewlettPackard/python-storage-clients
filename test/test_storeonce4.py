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

"""Tests for hpestorapi.StoreOnceG4 class."""

# pylint: disable=redefined-outer-name
# ^^^ this

import pytest
import requests
import responses

import hpestorapi


def test_exception_connection_error():
    """
    ConnectionError exception raising test.

    Wrong network address, firewall or rest api connection limit ...
    """
    so = hpestorapi.StoreOnceG4('wrong-address', 'user', 'password')
    with pytest.raises(requests.exceptions.ConnectionError):
        so.open()


@responses.activate
def test_exception_auth_error():
    """
    AuthError exception raising text.
    Wrong user or password.
    """
    responses.add(
        responses.POST,
        'https://1.1.1.1/pml/login/authenticatewithobject',
        status=401,
        content_type='application/json',
        json={},
    )

    so = hpestorapi.StoreOnceG4('1.1.1.1', 'Administrator', 'Admin')
    with pytest.raises(hpestorapi.storeonce4.AuthError):
        so.open()


@responses.activate
def test_get():
    """
    GET request
    """
    responses.add(
        responses.POST,
        'https://1.1.1.1/pml/login/authenticatewithobject',
        status=200,
        content_type='application/json',
        json={"access_token": "12345678890abcdefg"},
    )
    responses.add(
        responses.GET,
        'https://1.1.1.1/api/v1/management-services/local-storage/overview',
        status=200,
        content_type='application/json',
        json={
            "storageHealth": 0,
            "storageHealthString": "string",
            "simplifiedStatus": 0,
            "simplifiedStatusString": "string",
            "unconfiguredStorageBytes": 0,
            "configuredStorageBytes": 0,
            "usedBytes": 0,
            "freeBytes": 1024,
            "capacityLicensedBytes": 0,
            "capacityUnlicensedBytes": 0,
            "maxCapacityBytes": 0,
            "maxExpansions": 0
        },
    )
    responses.add(
        responses.DELETE,
        'https://1.1.1.1/pml/login/delete',
        status=204,
    )

    with hpestorapi.StoreOnceG4('1.1.1.1', 'Administrator', 'Admin') as so:
        so.open()
        status, data = so.get('/api/v1/management-services'
                              '/local-storage/overview')
        assert status == 200
        assert data['freeBytes'] == 1024
