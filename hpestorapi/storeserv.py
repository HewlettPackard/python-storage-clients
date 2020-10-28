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

"""Module with HPE StoreServ 3PAR disk array wrapper."""

import logging
import warnings
from urllib.parse import quote
from http import HTTPStatus

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from hpestorapi.base import BaseDevice, tracer, AuthError

if __name__ == "__main__":
    pass

logging.getLogger('hpestorapi.storeserv').addHandler(logging.NullHandler())
LOG = logging.getLogger('hpestorapi.storeserv')


class StoreServ(BaseDevice):
    """HPE 3PAR array implementation class."""

    def __init__(self, address, username, password, port=None, ssl=True,
                 verify=True):
        """
        HPE 3PAR object constructor.

        :param str address: Hostname or IP address of HPE 3PAR array
            management interface. Web Services API should be enabled for this
            array (disabled by default). To enable Web Services API check
            3PAR OS command: 'showwsapi'.
        :param str username: User name for 3PAR Web Services API. Creating a
            dedicated user with limited rights recommended. For example,
            if you do not need to create/modify/delete objects on a disk
            array, create a new user with a "browse" role. Running a script
            with a "3paradm" user is not recommended. To create a new user,
            check 3PAR OS command: 'createuser'.
        :param str password: Password for 3PAR Web Services API.
        :param int port: (optional) Custom port number for 3PAR Web Services
            API.
        :param bool ssl: (optional) Use secure https (True) or plain text
            http (False).
        :param bool|string verify: (optional) Either a boolean, controlling
            the Rest server's TLS certificate verification, or a string,
            where it is a path to a CA bundle. Default value: True.
        :return: None
        """
        super().__init__()

        self._address = address
        self._username = username
        self._password = password
        self._port = port
        self._ssl = ssl
        self._verify = verify

        # Session key. None, if there is not active session.
        self._key = None

        # Default request headers
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'en'
        }

    def __del__(self):
        """HPE 3PAR object destructor."""
        # Close active Rest API session
        if self._key is not None:
            self.close()

    @tracer
    def _query(self, url, method, **kwargs):
        """
        Perform HTTP request to HPE 3PAR array.

        :param str url: URL address. For example: 'system' or 'volumes'.
            Static part of url is generated automatically.
        :param str method: HTTP method. Could be 'GET', 'POST', 'DELETE' or
            'PUT'.
        :param float|tuple timeout: (optional) Like :attr:`StoreServ.delay`
            but only for one query.
        :rtype: tuple(int, dict)
        :return: Dictionary with HTTP status code and json data.
            For example: dict('status':200, 'data':{'key':'value'}).
            Second value may be None if 3PAR array returns no message body,
        """
        # Set connection delay and read delay
        timeout = kwargs.pop('timeout', self.timeout)

        # Add default and auth headers to parameter list
        kwargs.setdefault('headers', dict())
        kwargs['headers'].update(self._headers)

        # Prepare request
        path = '%s/%s' % (self._base_url, url.strip('/'))
        request = requests.Request(method, path, **kwargs)
        prep = request.prepare()
        LOG.debug('%s(`%s`)', method, prep.url)
        LOG.debug('Request body = `%s`', prep.body)

        # Perform request with runtime measuring
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            try:
                session = requests.Session()
                resp = session.send(prep, timeout=timeout, verify=self._verify)
                deltafmt = '%d.%d sec' % (resp.elapsed.seconds,
                                          resp.elapsed.microseconds // 1000)
            except Exception as error:
                LOG.fatal('Cannot connect to StoreServ device. %s',
                          repr(error))
                raise

        # Check Rest service response
        if resp.status_code not in [HTTPStatus.OK,
                                    HTTPStatus.CREATED,
                                    HTTPStatus.ACCEPTED,
                                    HTTPStatus.NO_CONTENT]:
            LOG.warning('Return code %s, response delay %s',
                        resp.status_code,
                        deltafmt)
            LOG.warning('resp.content=%s', resp.content)
            LOG.warning('resp.reason=%s', resp.reason)
        else:
            LOG.debug('StoreServ return status %s, delay %s',
                      resp.status_code,
                      deltafmt)

        # Check response JSON body is exist
        try:
            jdata = resp.json()
        except ValueError:
            if resp.content:
                LOG.warning('Cannot decode JSON. Source string: "%s"',
                            resp.content)
            return resp.status_code, None

        # Check wsapi session key expiration error
        if self.__is_token_expired(resp):
            # Just forget about current (inactive) session
            self._headers.pop('X-HP3PAR-WSAPI-SessionKey', None)
            self._key = None

            # Generate new session and replay last query
            try:
                self.open()
                replay = self._query(url, method, **kwargs)
            except Exception as error:
                LOG.fatal('Cannot open new WSAPI session. Exception: %s',
                          repr(error))
                raise error
            else:
                LOG.debug('Request replay success.')
                return replay

        return resp.status_code, jdata

    @staticmethod
    def __is_token_expired(response=None) -> bool:
        """
        Check Rest server response for session key expiration error.

        :param requests.Response() response: Rest server response.
        :rtype: bool
        :return: `True` - if session key was expired, `False` in all other
            cases.
        """
        if not isinstance(response, requests.Response):
            LOG.error('Unexpected object type. Must be `requests.Response()`. '
                      'Skipping session expiration check.')
            return False

        try:
            body = response.json()
        except ValueError:
            return False

        if (response.status_code == HTTPStatus.FORBIDDEN) and \
                (body.get('code', None) == 6):
            LOG.debug('Session expiration occurs. Session key is invalid.')
            return True

        return False

    @tracer
    def open(self) -> None:
        """
        Open new Rest API session for HPE 3PAR array.

        Call it prior any other requests. Call :meth:`StoreServ.close` if
        you do not plan to use a session anymore, because 3PAR array has an
        active sessions limit.

        Should any trouble occur, please manually check that:

            * 3PAR Web services API are enabled on the array (3PAR OS
              command: 'showwsapi')
            * Array credentials (username and password)
            * 3PAR  array management address is correct and available
            * Debug logs generated by a python logging module

        :return: None
        """
        auth = {'user': self._username, 'password': self._password}
        status, data = self.post('credentials', body=auth)
        if status == HTTPStatus.CREATED:
            # 201 (created) => Session succefully created
            self._headers.update({'X-HP3PAR-WSAPI-SessionKey': data['key']})
            self._key = data['key']
        elif status == HTTPStatus.FORBIDDEN:
            # 403 (forbidden) => Wrong user or password
            raise AuthError('Cannot connect to StoreServ. '
                            'Authentification error: %s', data['desc'])

    @tracer
    def close(self) -> None:
        """
        Close Rest API session.

        No need to run it manually when context manager is used (block \
        ``with .. as ..:``).

        :return: None
        """
        # There is not active session
        if self._key is None:
            LOG.debug('There is not active session - skipping session close.')
            return

        # Try to close active session
        path = f'credentials/{self._key}'
        try:
            self.delete(path)
        except Exception as error:
            LOG.warning('Cannot close StoreServ 3PAR session '
                        'gracefully. Exception occured: %s',
                        repr(error))

        self._headers.pop('X-HP3PAR-WSAPI-SessionKey')
        self._key = None

    def get(self, url, query=None):
        """
        Make a HTTP GET request to HPE 3PAR array. Method used to get \
        information about objects.

        :param str url: URL address. The static part of the URL address is
            generated automatically. Example of a valid URL: 'system' or
            'volumes'. All available URLs and requests results are described
            in "HPE 3PAR Web Services API Developer's Guide".
        :param str query: (optional) Query filter specification (see "WSAPI
            query syntax" in "HPE 3PAR Web Services API Developer's Guide").
        :rtype: tuple(int, dict)
        :return: Tuple with HTTP status code and dict with request result.
            For example: (200, {'key':'value'}).
        """
        # Perform get request with query filter
        if query is not None:
            return self._query(url, 'GET', params=quote(f'query="{query}"'))

        # Perform simple get request
        return self._query(url, 'GET')

    def post(self, url, body):
        """
        Make a HTTP POST request to HPE 3PAR array. Method used to create new \
        objects.

        :param str url: URL address. The static part of the URL address is
            generated automatically. Example of a valid URL: 'system' or
            'volumes'. All available URLs, request parameters and results
            are described in "HPE 3PAR Web Services API Developer's Guide".
        :param dict body: Request parameter, used to create new array object.
        :rtype: tuple (int, dict)
        :return: Tuple with HTTP status code and dict with request result.
            For example: (201, {'key':'value'}). Second value may be None if
            3PAR array returns no message body.
        """
        return self._query(url, 'POST', json=body)

    def delete(self, url):
        """
        Make a HTTP DELETE request to HPE 3PAR array.

        :param str url: URL address. The static part of the URL address is
            generated automatically. Example of a valid URL: 'system' or
            'volumes'. All available URLs, request parameters and results are
            described in "HPE 3PAR Web Services API Developer's Guide".
        :return: Tuple with HTTP status code and dict with request result. For
            example: (200, {'key':'value'}). Second value may be None if 3PAR
            array returns no message body.
        """
        return self._query(url, 'DELETE')

    def put(self, url, body):
        """
        Make a HTTP PUT request to HPE 3PAR array.

        :param str url: URL address. The static part of the URL address is
            generated automatically. Example of a valid URL: 'system' or
            'volumes'. All available URLs, request parameters and results are
            described in "HPE 3PAR Web Services API Developer's Guide".
        :param dict body: Request parameter, used to modify an array object.
        :rtype: tuple(int, dict)
        :return: Tuple with HTTP status code and dict with request result. For
            example: (200, {'key':'value'}). Second value may be None if 3PAR
            array returns no message body.
        """
        return self._query(url, 'PUT', json=body)

    @property
    def _base_url(self) -> str:
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        # URL Protocol
        proto = 'https' if self._ssl else 'http'

        # Device port number
        if self._port is None:
            port = 8080 if self._ssl else 8008
        else:
            port = self._port

        return f'{proto}://{self._address}:{port}/api/v1'

    def __enter__(self):
        """Create and return 3PAR object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Destroy 3PAR object."""
        # Close active Rest API session
        if self._key is not None:
            self.close()
