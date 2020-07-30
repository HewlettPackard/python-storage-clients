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

"""Module with HPE XP disk array wrapper."""

import logging
import warnings

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from hpestorapi.base import BaseDevice, AuthError, ParameterError

if __name__ == "__main__":
    pass

logging.getLogger('hpestorapi.xp').addHandler(logging.NullHandler())
LOG = logging.getLogger('hpestorapi.xp')


class ConfManager(BaseDevice):
    """Base class for all Configuration Manager objects."""

    def __init__(self, address, port=None, ssl=True):
        """Initialize Configuration manager object."""
        super().__init__()

        self.cvae_addr = address
        self.cvae_port = port
        self.cvae_ssl = ssl

        self._headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    @property
    def _base_url(self) -> str:
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        proto = 'https' if self.cvae_ssl else 'http'

        if self.cvae_port is None:
            port = 25451 if self.cvae_ssl else 25450
        else:
            port = self.cvae_port

        return f'{proto}://{self.cvae_addr}:{port}/ConfigurationManager'

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<class hpestorapi.{class_name}(address={self.cvae_addr})>'

    def _query(self, url, method, **kwargs):
        # Copy allowed args to options dict
        options = dict()
        allowed = ['params',
                   'json',
                   'headers',
                   'auth',
                   'delay',
                   'verify',
                   'cert']
        for key in kwargs:
            if key in allowed:
                options[key] = kwargs[key]

        # Add standart HTTP and auth headers to parameter list
        if kwargs.get('headers') is not None:
            options['headers'].update(self._headers)
        else:
            options['headers'] = self._headers

        # By default SSL cert checking is disabled
        certcheck = kwargs.get('verify', False)

        # Set HTTP delay (if not set by user)
        timeout = kwargs.get('delay', self.timeout)

        # Prepare request
        path = f'{self._base_url}/{url}'
        req = requests.Request(method, path, **options)
        prep = req.prepare()
        LOG.debug('%s(`%s`)', method, path)

        # Perform request with runtime measuring
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            try:
                session = requests.Session()
                resp = session.send(prep, verify=certcheck, timeout=timeout)
                deltafmt = '%d.%d sec' % (resp.elapsed.seconds,
                                          resp.elapsed.microseconds // 1000)
            except Exception as error:
                LOG.fatal('Cannot connect to Configuration Manager. %s',
                          error)
                raise error

        # Check Rest service response
        if resp.status_code != requests.codes.ok:
            LOG.warning('Return code %s, response delay %s',
                        resp.status_code,
                        deltafmt)
            LOG.warning('resp.content=%s', resp.content)
            LOG.warning('resp.reason=%s', resp.reason)
        else:
            LOG.debug('Rest server return status %s, delay %s',
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


class CommandViewAE(ConfManager):
    """Command View Advanced Edition object."""

    def device_reg(self, svp, serialnum, username, password, gen='XP7'):
        """Register new XP storage array."""
        LOG.debug('Trying to register new storage device on Configuration '
                  'manager. Serial Number:%s, Generation=%s.',
                  serialnum,
                  gen)

        # Perform device registration
        param = {
            'svpIp': svp,
            'serialNumber': serialnum,
            'model': gen}
        status, _ = self._query(
            'v1/objects/storages',
            method='POST',
            json=param,
            auth=(username, password))

        if status == requests.codes.ok:
            LOG.info('Storage device succefully registered in '
                     'Configuration manager.')
        else:
            LOG.warning('Storage device registration failure. Serial '
                        'Number:%s, Generation=%s.',
                        serialnum,
                        gen)

        return status

    def device_unreg(self, serialnum, username, password):
        """Remove XP storage array registration."""
        LOG.debug('Trying to remove storage device registration on '
                  'Configuration manager. Serial Number:%s.',
                  serialnum)

        array = self.device_find(serialnum)
        if array is None:
            LOG.info('Cannot remove storage device registration from '
                     'Configuration Manager database. Storage system not '
                     'found. Serial Number:%s',
                     serialnum)
        else:
            path = 'v1/objects/storages/%s' % array['storageDeviceId']
            status, _ = self._query(path,
                                    method='DELETE',
                                    auth=(username, password))
            if status == requests.codes.ok:
                LOG.info('Storage system registration sucessfully removed '
                         'from Configuration manager database. Serial '
                         'Number:%s',
                         serialnum)
                return True

            LOG.error('Cannot remove storage system registration from '
                      'Configuration Manager database. Rest API server '
                      'return code:%s. Serial Number:%s',
                      status, serialnum)

        return False

    def device_find(self, serialnum):
        """Find XP storage array in list of registered."""
        status, data = self._query('v1/objects/storages', method='GET')
        if status == requests.codes.ok:
            for array in data.get('data'):
                if str(serialnum) == str(array.get('serialNumber')):
                    return array
        return None


class Xp(ConfManager):
    """XP7 / P9500 class implementation."""

    def __init__(self, cvae, svp, serialnum, username, password, gen='XP7',
                 port=23451, ssl=True):
        """
        HPE XP constructor.

        :param str cvae: Hostname or IP address of HPE Command View AE
            Configuration Manager.
        :param str svp: Hostname or IP address of Service Processor (SVP).
        :param str serialnum: Array serial number (5 or 6 digits)
        :param str username: User name for HPE XP disk array. Creating a
            dedicated user with limited rights is recommended. Using
            "arrayadmin" account is a bad practice.
        :param str password: Password for HPE XP disk array.
        :param str gen: (optional) Disk array generation. Should be P9500 or
            XP7. Default value: XP7.
        :param int port: (optional) Command View AE configuration manager
            port. Default value: 23451
        :param bool ssl: (optional) Use secure https (True) or plain http (
            False). Default value: True.
        :return: None.
        """
        super().__init__(cvae, port, ssl)
        self._session = {'id': None, 'token': None}
        self._gen = gen
        self._svp = svp
        self._serialnum = serialnum
        self._username = username
        self._password = password

    def __del__(self):
        self.close()

    def open(self):
        """
        Open a new Rest API session for a HPE XP array.

        Call it prior any other requests. Call :meth:`Xp.close()` if you do not
        plan to use session anymore.

        :rtype: bool
        :return: Return True, if disk array provides a valid session key.
        """
        status, data = self.post(
            'sessions',
            auth=(self._username, self._password)
        )
        if status == requests.codes.ok:
            # Session succefully opened
            LOG.info('Access token and session ID succefully received for '
                     'storage device. Serial Number:%s', self._serialnum)
            self._session['id'] = data['sessionId']
            self._session['token'] = data['token']
            self._headers['Authorization'] = 'Session ' + data['token']
            return True
        if status == requests.codes.not_found:
            # Storage is not registered in Configuration Manager
            LOG.info('Storage device is not registered in Configuration '
                     ' manager yet. Lets try to resolve. Serial Number:',
                     self._serialnum)
            if data['messageId'] == 'KART30070-E':
                cvae = CommandViewAE(self.cvae_addr, self.cvae_port,
                                     self.cvae_ssl)
                status = cvae.device_reg(self._svp,
                                         self._serialnum,
                                         self._username,
                                         self._password,
                                         self._gen)
                if status == requests.codes.ok:
                    return self.open()
        elif status == requests.codes.unauthorized:
            LOG.fatal('Cannot open Rest API session - wrong user name or '
                      'password. Serial Number:%s',
                      self._serialnum)
            raise AuthError('''
                            id: "{id}",
                            url: "{url}",
                            message: "{msg}",
                            cause: "{cause}",
                            solution: "{sol}"
                            '''.format(id=data['messageId'],
                                       url=data['errorSource'],
                                       msg=data['message'],
                                       cause=data['cause'],
                                       sol=data['solution'])
                            )

        return False

    def close(self, passive=False):
        """
        Close Rest API session.

        :param bool passive: (optional) Do not try to close session in the
            array. Revoke the client session key after session timed out. Use
            this parameter only for method overriding in subclasses. There is no
            need of using it, as class implementation manages the session
            life cycle. Default value: False.
        :return: None
        """
        # Only for active session discard
        if (self._session.get('id') is not None) and (not passive):
            LOG.debug('Lets close Rest API session. '
                      'Serial Number:%s', self._serialnum)
            self.delete('sessions/%s' % self._session['id'])

        # Clear session info (for all sessions)
        self._session['id'] = self._session['token'] = None

    def get(self, url, **kwargs):
        """
        Make a HTTP GET request to HPE XP array. Use this method to get \
        information about array objects.

        :param str url: URL address. Th static part of the URL address is
            generated automatically. Example ofvalid URL: 'pools',
            'parity-groups', 'ldevs'. All available URL's and requests result
            are described in "HPE XP7 Command View Advanced Edition REST API
            Reference Guide".
        :param dict params: (optional) Dictionary with query filter
            parameters. Described in 'Query parameters' section of "HPE XP7
            Command View Advanced Edition REST API Reference Guide".
        :param dict json: (optional) A JSON serializable object send in the
            request body.
        :param float timeout: (optional) Number of seconds that Rest API
            client waits for a response from the Rest server before
            generating a timeout exception. Default value: :attr:`Xp.timeout`.
        :param bool verify: (optional) Either a boolean, controlling
            the Rest server's TLS certificate verification, or a string,
            where it is a path to a CA bundle. Default value: False (no
            certificate verification).
        :param str cert: (optional)  String with path to ssl client
            certificate file (.pem) or tuple pair (‘cert’, ‘key’).
        :rtype: (int, {})
        :return: Tuple with HTTP status code and dict with request result.
            For example: (200, {‘key’:’value’})
        """
        return self._query(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        """
        Make a HTTP POST request to HPE XP array. Use this method to create \
            a new object.

        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param float timeout: (optional) Number of seconds that Rest API
            client waits for a response from the Rest server before
            generating a timeout exception. Default value: :attr:`Xp.timeout`.
        :param bool verify: (optional) Either a boolean, controlling
            the Rest server's TLS certificate verification, or a string,
            where it is a path to a CA bundle. Default value: False (no
            certificate verification).
        :param str cert: (optional)  String with path to ssl client
            certificate file (.pem) or tuple pair (‘cert’, ‘key’).
        :rtype: (int, {})
        :return: Tuple with HTTP status code and dict with request result.
            For example: (200, {‘key’:’value’})
        """
        return self._query(url, 'POST', **kwargs)

    def delete(self, url, **kwargs):
        """
        Make a HTTP DELETE request to HPE XP array. Use this method to remove \
        objects.

        :param dict json: (optional) A JSON serializable object send in the
            request body.
        :param float timeout: (optional) Number of seconds that Rest API
            client waits for a response from the Rest server before
            generating a timeout exception. Default value: :attr:`Xp.timeout`.
        :param bool verify: (optional) Either a boolean, controlling
            the Rest server's TLS certificate verification, or a string,
            where it is a path to a CA bundle. Default value: False (no
            certificate verification).
        :param str cert: (optional)  String with path to ssl client
            certificate file (.pem) or tuple pair (‘cert’, ‘key’).
        :rtype: (int, {})
        :return: Tuple with HTTP status code and dict with request result.
            For example: (200, {‘key’:’value’})
        """
        return self._query(url, 'DELETE', **kwargs)

    def put(self, url, **kwargs):
        """
        Perform HTTP PUT request to HPE XP array.

        :param dict json: (optional) A JSON serializable object to send in
            the body of request.
        :param float timeout: (optional) Number of seconds that Rest API
            client waits for a response from the Rest server before
            generating a timeout exception. Default value: :attr:`Xp.timeout`.
        :param bool verify: (optional) Either a boolean, controlling
            the Rest server's TLS certificate verification, or a string,
            where it is a path to a CA bundle. Default value: False (no
            certificate verification).
        :param str cert: (optional)  String with path to ssl client
            certificate file (.pem) or tuple pair (‘cert’, ‘key’).
        :rtype: (int, {})
        :return: Tuple with HTTP status code and dict with request result.
            For example: (200, {‘key’:’value’})
        """
        return self._query(url, 'PUT', **kwargs)

    def _query(self, url, method, **kwargs):
        status, data = ConfManager._query(self, url, method, **kwargs)

        # If session was expired
        if self._is_expired(status, data):
            # Clear old session record
            self._headers.pop('Authorization')

            # Get new session token
            self.close(passive=True)
            self.open()

            # Replay last request
            return ConfManager._query(self, url, method, **kwargs)

        return status, data

    def _is_expired(self, status, data):
        """Check Rest API session timeout error."""
        # Authorization token wasnt received before
        if self._headers.get('Authorization') is None:
            return False

        # If provided token is timed out
        if (status == requests.codes.unauthorized) and \
                (data.get('messageId') == 'KART40047-E'):
            LOG.info('Looks like current access token and session are '
                     ' expired. Session ID:%s, Serial Number:%s',
                     self._session['id'],
                     self._serialnum)
            return True

        return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<class hpestorapi.{class_name}(dev={self._serialnum})>'

    @property
    def _base_url(self) -> str:
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        base = super()._base_url

        # Generate device id
        if self._gen == 'P9500':
            dev = '7' + str(self._serialnum).rjust(11, '0')
        elif self._gen == 'XP7':
            dev = '8' + str(self._serialnum).rjust(11, '0')
        else:
            LOG.fatal('Unknown array generation. gen="%s"', self._gen)
            raise ParameterError(f'Unknown array generation. gen={self._gen}.')

        return f'{base}/v1/objects/storages/{dev}'
