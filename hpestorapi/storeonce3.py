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
.. module:: hpestorapi.storeonce3
    :synopsis: Module with HPE StoreOnce Gen3 disk backup device

.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

import copy
import logging
from os.path import join, normpath, isdir, isfile
import pickle
import socket
import warnings
from xml.etree import ElementTree as ETree

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

if __name__ == "__main__":
    pass

LOG = logging.getLogger('hpestorapi.storeonce')


class StoreOnceG3:
    """
        HPE StoreOnce Gen 3 disk backup device implementation class.
    """

    def __init__(self, address, user, password, cookie_dir=None, port=443):
        """
        HPE StoreOnceG3 constructor.

        :param str address: Hostname or IP address of HPE StoreOnce disk
            backup device.
        :param str user: Username for HPE StoreOnce disk backup device.
        :param str password: Password for HPE StoreOnce disk backup device.
        :param str cookie_dir: User name for HPE StoreOnce disk backup device.
            Its recommended to create dedicated user with limited rights. It's
            a bad idea to use "Admin" account.
        :param int port: (optional) Custom port number for StoreOnce device.
        :return: None.
        """
        self._address = address
        self._user = user
        self._password = password
        self._port = port

        # Default timeouts:
        # ConnectionTimeout = 1 second
        # ReadTimeout = infinity
        self._timeout = (1.0, None)

        self._auth_cookies = requests.cookies.RequestsCookieJar()

        # Get cookile file path
        if cookie_dir is not None:
            if os.path.isdir(cookie_dir):
                ip_addr = socket.gethostbyname(self._address.strip())
                self._cookie_file = f'{cookie_dir}/{ip_addr}.cookie'
                LOG.debug('Cookie filename:%s', self._cookie_file)
            else:
                LOG.warning('Cookie directory is not available. Path: %s',
                            cookie_dir)

    @property
    def _base_url(self):
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        url = f'https://{self._address}:{self._port}/storeonceservices'
        return url

    def __del__(self):
        self._cookie_save()

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<class hpestorapi.{class_name}(address={self._address})>'

    def query(self, url, method, **kwargs):
        # Filter allowed kwargs to option dict
        allowed = ['params',
                   'json',
                   'auth',
                   'cert',
                   'headers',
                   'cookies']
        option = dict()
        for key in kwargs:
            if key in allowed:
                option[key] = copy.deepcopy(kwargs[key])

        # Add standard headers for all requests
        headers_default = {'Accept': 'text/xml',
                           'Content-Type': 'text/xml'}
        if 'headers' in option.keys():
            headers_default.update(option['headers'])
        option['headers'] = headers_default
        LOG.debug('headers=', option['headers'])

        # Add auth cookie for all requests
        if 'cookies' not in option.keys():
            option['cookies'] = requests.cookies.RequestsCookieJar()
        option['cookies'].update(self._auth_cookies)

        # By default SSL cert checking is disabled
        certcheck = kwargs.get('verify', False)

        # Set connection and read timeout (if not set by user)
        timeout = kwargs.pop('timeout', self.timeout)

        # Prepare request
        path = '%s/%s/' % (self._base_url, f'{url}'.strip('/'))
        session = requests.Session()
        request = requests.Request(method, path, **option)
        prepped = session.prepare_request(request)
        resp = requests.Response()
        LOG.debug('%s("%s", timeouts=%s)', method, path, timeout)

        # Perform request
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=InsecureRequestWarning)
            try:
                resp = session.send(prepped, verify=certcheck,
                                    timeout=timeout)
                deltafmt = '%d.%d sec' % (resp.elapsed.seconds,
                                          resp.elapsed.microseconds // 1000)
            except Exception as error:
                LOG.fatal(error)
                raise error

        LOG.debug('StoreOnce return status %s, delay %s',
                  resp.status_code,
                  deltafmt)

        # Check Rest service response
        if resp.status_code == requests.codes.unauthorized:
            # Replay last query
            if self._is_expired(resp):
                if self.open(cookie_load=False):
                    return self.query(url, method, **kwargs)
        else:
            LOG.warning('resp.url=%s', resp.url)
            LOG.warning('resp.content=%s', resp.content)
            LOG.warning('resp.reason=%s', resp.reason)

        return resp

    def get(self, url, **kwargs):
        """
        Perform HTTP GET request to HPE Storeonce disk backup device. Method
        used to get information about objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'cluster' or 'cluster/servicesets'. All available url's
            and requests result are described in "HPE StoreOnce 3.18.2 REST
            API developer Guide"
        :param RequestsCookieJar filter: (optional) Filter cookies, that was
            generated by method :meth:`StoreOnceG3.filter`
        :param int timeout: (optional)
        :rtype: (int, string)
        :return: Tuple with HTTP status code and xml string with request
            result. For example: (200, '<xml> ... </xml>').
        """
        if filter is not None:
            # TODO
            pass

        resp = self.query(url, 'GET', **kwargs)
        return (resp.status_code, resp.content.decode('utf-8'))

    def post(self, url, **kwargs):
        """
        Perform HTTP POST request to HPE Storeonce disk backup device. Method
        used to create new objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'cluster' or 'cluster/servicesets'. All available url's
            and requests result are described in "HPE StoreOnce 3.18.2 REST
            API developer Guide"
        :rtype: (int, string)
        :return: Tuple with HTTP status code and xml string with request
            result. For example: (200, '<xml> ... </xml>').
        """
        resp = self.query(url, 'POST', **kwargs)
        return (resp.status_code, resp.content.decode('utf-8'))

    def put(self, url, **kwargs):
        """
        Perform HTTP PUT request to HPE Storeonce disk backup device. Method
        used to update objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'cluster' or 'cluster/servicesets'. All available url's
            and requests result are described in "HPE StoreOnce 3.18.2 REST
            API developer Guide"
        :param int timeout: (optional)
        :rtype: (int, string)
        :return: Tuple with HTTP status code and xml string with request
            result. For example: (200, '<xml> ... </xml>').
        """
        resp = self.query(url, 'PUT', **kwargs)
        return (resp.status_code, resp.content.decode('utf-8'))

    def delete(self, url, **kwargs):
        """
        Perform HTTP DELETE request to HPE Storeonce disk backup device. Method
        used to delete objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'cluster' or 'cluster/servicesets'. All available url's
            and requests result are described in "HPE StoreOnce 3.18.2 REST
            API developer Guide"
        :param int timeout: (optional)
        :rtype: (int, string)
        :return: Tuple with HTTP status code and xml string with request
            result. For example: (200, '<xml> ... </xml>').
        """
        resp = self.query(url, 'DELETE', **kwargs)
        return (resp.status_code, resp.content.decode('utf-8'))

    def open(self, cookie_load=True):
        if cookie_load:
            if self._cookie_load():
                return True

        resp = self.query('/cluster', 'GET', auth=(self._user, self._password))
        if resp.status_code == requests.codes.ok:
            self._auth_cookies = resp.cookies
            LOG.debug('Authentification success')
            return True

        LOG.fatal('Cant authentificate on storeonce appliance')
        return False

    def _cookie_load(self):
        if not hasattr(self, '_cookie_file'):
            return False

        if not os.path.isfile(self._cookie_file):
            LOG.info('Cant open cookie file. '
                     'Filename = "%s"', self._cookie_file)
            return False

        # Open cookie file
        try:
            file = open(self._cookie_file, 'rb')
        except OSError as error:
            LOG.error('Cant open cookies file. Filename = "%s"',
                      self._cookie_file)
            LOG.error(error)
            return False

        # Load cookie from file
        with file:
            try:
                cookie = pickle.load(file)
            except pickle.UnpicklingError:
                LOG.error('Cannot load cookies from cookie file. Broken file'
                          'format. Filename = "%s"', self._cookie_file)
                return False
            else:
                LOG.debug('Auth cookie succefully loaded from file.')

            if cookie:
                self._auth_cookies = cookie
                LOG.debug('Cookies successfully loaded from file.')
                return True

        return False

    def _is_expired(self, request):
        page = ETree.fromstring(request.content)
        msg = page.find('./errors/error/message')
        if msg is not None:
            if 'Your session has expired.' in msg.text:
                LOG.debug('Session has expired.')
                return True

        LOG.warning('Session has not expired')
        return False

    def _cookie_save(self):
        if not hasattr(self, '_cookie_file'):
            return False

        # Truncate cookie file
        try:
            file = open(self._cookie_file, 'wb')
            file.truncate()
        except OSError as error:
            LOG.error('Cannot write to cookie file. '
                      'Filename = "%s"', self._cookie_file)
            LOG.error(error)
            return False

        # Save auth cookies to file
        with file:
            try:
                pickle.dump(self._auth_cookies, file)
            except pickle.PicklingError as error:
                LOG.error('Cannot save cookies to file.')
                LOG.error(error)
                return False

        LOG.debug('Cookie saved to file succefully.')
        return True

    def iterate(self, url, items):
        return Iterator(self, url, items)

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
            client waits for response from HPE StoreOnce Gen 3
            before timeout exception generation. You can use
            different timeouts for connection setup and for getting
            first piece of data. In this case, you should use
            tuple(float, float) with first value - connection
            timeout and the second value - read timeout. Or if
            you want to use same values for both type of timeouts,
            you can use one float value. 'None' value can be used
            instead to wait forever for a device response. Default
            value: (1, None).
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Iterator:
    def __init__(self, device, url, items):
        self.device = device
        self.url = url
        self.items = items

        # Data page content
        self.page = None

        # Current element index on the data page
        self.index = 0

        # Is there any pages after current
        self.last = True

        # Waypoint cookies for pagination
        self.cookies = None

    def __next__(self):
        if self.page is None:
            # Request first data page
            resp = self.device.query(self.url, 'GET')
        else:
            self.index += 1

            # Return item from current data page
            if len(self.page) > self.index:
                return self.page[self.index]

            # Request next data page
            if not self.last:
                resp = self.device.query(self.url,
                                         'GET',
                                         cookies=self.cookies,
                                         params={'list': 'next',
                                                 'count': 1000}
                                         )
                self.index = 0
            else:
                LOG.debug('It was last page. Iteration stopped.')
                raise StopIteration

        xmldoc = ETree.fromstring(resp.content)

        # Save waypoint cookies for paginated answers
        hasnext = xmldoc.find('./properties/nextPageAvailable')
        if hasnext is not None:
            # Multipage request
            if hasnext.text == 'true':
                self.cookies = resp.cookies
                self.last = False
            elif hasnext.text == 'false':
                # Last page reached
                self.last = True
            else:
                LOG.fatal('Unknown value in multipage answer '
                          'nextPageAvailable=%s', hasnext.text)

        # Parse device response
        self.page = []
        for item in xmldoc.findall(self.items):
            self.page.append(ETree.tostring(item, method="xml").decode('utf-8'))

        # There aren't items with requested tag
        if not self.page:
            LOG.warning('Cannot find requested tags in server response. '
                        'Tag: "%s"', self.items)
            raise StopIteration

        # Return first item from current data page
        return self.page[0]

    def __iter__(self):
        return self
