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
.. module:: hpestorapi.storeserv
    :synopsis: Module with HPE 3PAR disk array wrapper

.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

import logging
import warnings

from urllib.parse import quote
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


if __name__ == "__main__":
    pass

LOG = logging.getLogger('hpestorapi.storeserv')


class StoreServ:
    """
        HPE 3PAR array implementation class.
    """

    def __init__(self, address, username, password, port=None, ssl=True, verify=True):
        """
        HPE 3PAR constructor.

        :param str address: Hostname or IP address of HPE 3PAR array
            (management address). Web Services API should be enabled for this
            array (disabled by default). To enable Web Services API you should
            check 3PAR OS command: showwsapi.
        :param str username: User name for 3PAR Web Services API. Its
            recommended to create dedicated user with limited rights. For
            example, if you dont need to create/modify/delete objects on disk
            array, you should create new user with "browse" role. Of coarse,
            your script can work with "3paradm" user ("super" role), but
            its a bad idea. To create new user, you should check 3PAR OS
            command: createuser.
        :param str password: Password for 3PAR Web Services API.
        :param int port: (optional) Custom port number for 3PAR Web Services
            API.
        :param bool ssl: (optional) Use secure https (True) or plain text
            http (False).
        :param bool|string verify: (optional) Either a boolean, in which case it
            controls whether we verify the Rest server’s TLS certificate,
            or a string, in which case it must be a path to a CA
            bundle to use. By default: True.
        :return: None
        """
        self._address = address
        self._username = username
        self._password = password
        self._port = port
        self._ssl = ssl
        self._verify = verify

        # Session key. None, if there is not active session.
        self._key = None

        # Default timeouts:
        # ConnectionTimeout = 1 second
        # ReadTimeout = infinity
        self._timeout = (1, None)

        # Default request headers
        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'en'
        }

    def __del__(self):
        # Perform session close
        if self._key is not None:
            self.close()

    def _query(self, url, method, **kwargs):
        """
        Perform HTTP request to HPE 3PAR array.

        :param str url: URL address. For example: 'system' or 'volumes'.
            Static part of url is generated automatically.
        :param str method: HTTP method. Could be 'GET', 'POST', 'DELETE' or
            'PUT'.
        :param float|tuple timeout: (optional) Like :attr:`StoreServ.timeout`
            but only for one query.
        :rtype: tuple(int, dict)
        :return: Dictionary with HTTP status code and json data.
            For example: dict('status':200, 'data':{'key':'value'}).
            Second value may be None if 3PAR array returns no message body,
        """
        # Set connection and read timeout (if not set by user for current request)
        timeout = kwargs.pop('timeout', self._timeout)

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
        if resp.status_code not in [200, 201, 202, 204]:
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
            return resp.status_code, None  # (status, data)

        # Check wsapi session timeout error
        if (resp.status_code == 403) and (jdata.get('code', None) == 6):
            if self._key is not None:
                LOG.info('Session timeout occurs. Session key is invalid. '
                         'Try to get new one.')

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
                raise
            else:
                LOG.debug('Request replay success.')
                return replay

        return resp.status_code, jdata

    def open(self):
        """
        Open new Rest API session for HPE 3PAR array. You should call it prior
        any other requests. Do not forget to call :meth:`StoreServ.close` if
        you don't plan to use session anymore, because 3PAR array has active
        sessions limit.

        If some troubles occurs you should manually check:

            * 3PAR Web services API are enabled on array (3PAR OS
              command: 'showwsapi')
            * Array credentials (username and password)
            * 3PAR  array management address is correct and available
            * Debug logs generated by python logging module

        :return: None
        """
        auth = {'user': self._username, 'password': self._password}
        status, data = self.post('credentials', body=auth)
        if status == 201:
            # 201 (created) => Session succefully created
            self._headers.update({'X-HP3PAR-WSAPI-SessionKey': data['key']})
            self._key = data['key']
        elif status == 403:
            # 403 (forbidden) => Wrong user or password
            raise AuthError('Cannot connect to StoreServ. '
                            'Authentification error: %s', data['desc'])

    def close(self):
        """
        Close Rest API session.

        :return: None
        """
        # There isnt active session
        if self._key is None:
            LOG.debug('There isnt active session - skipping session close.')
            return

        # Try to close active session
        path = 'credentials/' + self._key
        try:
            self.delete(path)
        except Exception as error:
            LOG.warning('Cannot close StoreServ 3PAR session '
                        'gracefully. Exception occured: %s',
                        repr(error))
        else:
            self._headers.pop('X-HP3PAR-WSAPI-SessionKey')
            self._key = None

    def get(self, url, query=None):
        """
        Perform HTTP GET request to HPE 3PAR array. Method used to get
        information about objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'system' or 'volumes'. All available url's and requests
            result are described in "HPE 3PAR Web Services API Developer's
            Guide"
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
        Perform HTTP POST request to HPE 3PAR array. Method used to create new
        objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'system' or 'volumes'. All available url's, request
            parameters and results are described in "HPE 3PAR Web Services API
            Developer's Guide"
        :param dict body: Request parameter, used to create new array object.
        :rtype: tuple (int, dict)
        :return: Tuple with HTTP status code and dict with request result.
            For example: (201, {'key':'value'}). Second value may be None if
            3PAR array returns no message body.
        """
        return self._query(url, 'POST', json=body)

    def delete(self, url):
        """
        Perform HTTP DELETE request to HPE 3PAR array.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'system' or 'volumes'. All available url's, request
            parameters and results are described in "HPE 3PAR Web Services API
            Developer's Guide"
        :return: Tuple with HTTP status code and dict with request result. For
            example: (200, {'key':'value'}). Second value may be None if 3PAR
            array returns no message body.
        """
        return self._query(url, 'DELETE')

    def put(self, url, body):
        """
        Perform HTTP PUT request to HPE 3PAR array.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'system' or 'volumes'. All available url's, request
            parameters and results are described in "HPE 3PAR Web Services
            API Developer's Guide"
        :param dict body: Request parameter, used to modify array object.
        :rtype: tuple(int, dict)
        :return: Tuple with HTTP status code and dict with request result. For
            example: (200, {'key':'value'}). Second value may be None if 3PAR
            array returns no message body.
        """
        return self._query(url, 'PUT', json=body)

    def _set_timeout(self, timeout):
        if isinstance(timeout, (float, int)):
            self._timeout = (timeout, timeout)
        elif isinstance(timeout, tuple):
            self._timeout = timeout

    def _get_timeout(self):
        return self._timeout

    timeout = property(_get_timeout, _set_timeout)
    """
        :var float|tuple timeout: Number of seconds that Rest API
            client waits for response from HPE StoreServ
            before timeout exception generation. You can use
            different timeouts for connection setup and for getting
            first piece of data. In this case, you should use
            tuple(float, float) with first value - connection
            timeout and the second value - read timeout. Or if
            you want to use same values for both type of timeouts,
            you can use one float value. 'None' value can be used
            instead to wait forever for a device response. Default
            value: (1, None)
    """

    @property
    def _base_url(self):
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
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._key is not None:
            self.close()


class AuthError(Exception):
    """ Authentification error """
