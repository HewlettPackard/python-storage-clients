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

"""Module with HPE StoreOnce Gen4 disk backup device."""

import logging
import os
import pathlib
import warnings

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from hpestorapi.base import BaseDevice, tracer, AuthError, ParameterError

if __name__ == "__main__":
    pass

logging.getLogger('hpestorapi.storeonce').addHandler(logging.NullHandler())
LOG = logging.getLogger('hpestorapi.storeonce')


class StoreOnceG4(BaseDevice):
    """HPE StoreOnce Gen 4 backup device implementation class."""

    def __init__(self, address, username, password):
        """
        HPE StoreOnce Gen 4 disk backup constructor.

        :param str address: Hostname or IP address of HPE StoreOnce
            device.
        :param str username: Username for HPE StoreOnce device.
        :param str password: Password for HPE StoreOnce device.
        :return: None.
        """
        super().__init__()

        self._address = address
        self._username = username
        self._password = password

        self._verify = False
        self._headers = {'Content-Type': 'application/json',
                         'Accept': 'application/json'}

    @tracer
    def _query(self, url, method, **kwargs):
        # Set SSL cert checking
        verify = kwargs.pop('verify', self._verify)

        # Set connection and read timeout (if not set by user)
        timeout = kwargs.pop('timeout', self.timeout)

        # Add standart and auth headers to parameter list
        kwargs.setdefault('headers', dict())
        kwargs['headers'].update(self._headers)

        # Prepare request
        path = '%s/%s' % (self._base_url(), url.strip('/'))
        LOG.debug('%s(`%s`)', method, path)
        request = requests.Request(method, path, **kwargs)
        prep = request.prepare()

        # Perform request with runtime measuring
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            try:
                session = requests.Session()
                resp = session.send(prep, timeout=timeout, verify=verify)
                deltafmt = '%d.%d sec' % (resp.elapsed.seconds,
                                          resp.elapsed.microseconds // 1000)
            except Exception as error:
                LOG.fatal('Cannot connect to StoreOnce device. %s',
                          error)
                raise error

        # Check Rest service response
        if resp.status_code not in [200, 201, 202, 204]:
            LOG.warning('Return code %s, response delay %s',
                        resp.status_code,
                        deltafmt)
            LOG.warning('resp.content=%s', resp.content)
            LOG.warning('resp.reason=%s', resp.reason)
        else:
            LOG.debug('StoreOnce return status %s, delay %s',
                      resp.status_code,
                      deltafmt)

        # Check JSON string and return response
        try:
            jdata = resp.json()
        except ValueError:
            if resp.content:
                LOG.warning('Cannot decode JSON. Source string: %s',
                            resp.content)
            return resp.status_code, None

        return resp.status_code, jdata  # success = True, data = json

    @tracer
    def open(self, verify=False):
        """
        Open new Rest API session for HPE StoreOnce Gen 4 disk backup.

        You should call it prior any other requests. Do not forget to call
            :meth:`StoreOnceG4.close()` if you don’t plan to use current
            session anymore.

        :param bool|str verify: (optional) Either a boolean, in which
            case it controls whether we verify the Rest server’s TLS
            certificate, or a string, in which case it must be a path to
            a CA bundle to use. By default: False (do not check
            certificate).
        :return: None
        """
        # Check verify parameter
        if isinstance(verify, bool):
            LOG.debug('SSL cert verification set to: %s', verify)

        elif isinstance(verify, str):
            LOG.debug('Trying to use custom server ssl certificate. '
                      'PEM file bundle path: %s', verify)

            # Lets try to check .pem file permissions
            pem = pathlib.Path(verify)
            if not pem.is_file():
                LOG.error('SSL certificate file (.pem) cannot be '
                          'opened. Wrong file path. Path: %s', verify)
            if not os.access(verify, os.R_OK):
                LOG.error('SSL certificate file (.pem) cannot be '
                          'opened. Wrong permission. Path: %s', verify)
        else:
            # Invalid type fot `verify` parameter
            LOG.fatal('Invalid type for `verify` parameter. Must be bool or '
                      'str.')
            raise ParameterError('Invalid type for verify parameter. '
                                 'Type: %s' % type(verify).__name__)

        # Message body for authentification request
        body = {'username': self._username,
                'password': self._password,
                'grant_type': 'password'}

        # Perform authentification request
        try:
            status, data = self.post('/pml/login/authenticatewithobject',
                                     json=body,
                                     verify=verify)
        except requests.exceptions.SSLError as error:
            LOG.fatal('SSL certificate verification error.')
            raise error

        # Check device response
        if status == 200:
            # 200 => Session succefully opened
            auth = {'Authorization': f'Bearer {data["access_token"]}'}
            self._headers.update(auth)
            self._verify = verify
        elif status == 401:
            # 401 => Wrong credentials
            LOG.fatal('Cannot open Rest API session for StoreOnce G4 device '
                      '- wrong user name or password. StoreOnce address: %s',
                      self._address)
            raise AuthError(data)

    @tracer
    def close(self):
        """
        Close Rest API session.

        You don't need to run it manually if you use context manager.

        :return: None
        """
        # Session was not opened before
        if self._headers.get('Authorization', None) is None:
            return

        # Lets try to close session on StoreOnce G4 device
        try:
            status, _ = self.delete('/pml/login/delete')
        except Exception as error:
            LOG.warning('Session was not closed properly. '
                        'Exception occured: %s', error)
        else:
            if status == 204:
                LOG.debug('Session succefully closed.')
            else:
                LOG.warning('Session was closed with status code: %d',
                            status)

    def get(self, url, **kwargs):
        """
        Perform HTTP GET request to HPE Storeonce G4 disk backup device.

        This method used to get information about objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: '/rest/alerts' or '/api/v1/management-services/licensing'.
            All available url's and requests result are described in
            `HPE StoreOnce REST API
            <https://hewlettpackard.github.io/storeonce-rest/>`_
        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param dict params: (optional) Dictionary with url encoded
            parameters.
        :param float|tuple timeout: (optional) How many second to wait for the
            Rest server response before giving up. By default use
            same value as :attr:`StoreOnceG4.timeout`.
        :rtype: tuple(int, dict())
        :return: Tuple with HTTP status code and dict with request
            result. For example: (200, {...}) or (204, None).
        """
        return self._query(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        """
        Perform HTTP POST request to HPE StoreOnce G4 disk backup device.

        This method used to create new object.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: '/rest/alerts' or '/api/v1/management-services/licensing'.
            All available url's and requests result are described in
            `HPE StoreOnce REST API
            <https://hewlettpackard.github.io/storeonce-rest/>`_
        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param dict params: (optional) Dictionary with url encoded
            parameters.
        :param float|tuple timeout: (optional) How many second to wait for the
            Rest server response before giving up. By default use
            same value as :attr:`StoreOnceG4.timeout`.
        :rtype: tuple(int, dict())
        :return: Tuple with HTTP status code and dict with request
            result. For example: (200, {...}) or (204, None).
        """
        return self._query(url, 'POST', **kwargs)

    def delete(self, url, **kwargs):
        """
        Perform HTTP DELETE request to HPE StoreOnce G4 disk backup device \
            array.

        This method used to remove objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: '/rest/alerts' or '/api/v1/management-services/licensing'.
            All available url's and requests result are described in
            `HPE StoreOnce REST API
            <https://hewlettpackard.github.io/storeonce-rest/>`_
        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param dict params: (optional) Dictionary with url encoded
            parameters.
        :param float|tuple timeout: (optional) How many second to wait for the
            Rest server response before giving up. By default use
            same value as :attr:`StoreOnceG4.timeout`.
        :rtype: tuple(int, dict())
        :return: Tuple with HTTP status code and dict with request
            result. For example: (200, {...}) or (204, None).
        """
        return self._query(url, 'DELETE', **kwargs)

    def put(self, url, **kwargs):
        """
        Perform HTTP PUT request to HPE StoreOnce G4 disk backup device array.

        This method used to modify objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: '/rest/alerts' or '/api/v1/management-services/licensing'.
            All available url's and requests result are described in
            `HPE StoreOnce REST API
            <https://hewlettpackard.github.io/storeonce-rest/>`_
        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param dict params: (optional) Dictionary with url encoded
            parameters.
        :param float|tuple timeout: (optional) How many second to wait for the
            Rest server response before giving up. By default use
            same value as :attr:`StoreOnceG4.timeout`.
        :rtype: tuple(int, dict())
        :return: Tuple with HTTP status code and dict with request
            result. For example: (200, {...}) or (204, None).
        """
        return self._query(url, 'PUT', **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<class hpestorapi.{class_name}({self._address})>'

    def _base_url(self) -> str:
        return f'https://{self._address}'
