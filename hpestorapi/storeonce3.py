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
import warnings
from xml.etree import ElementTree as ETree

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from .storeonce3_utils import load_cookie, save_cookie

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
        :param str cookie_dir: (optional) Directory for authentification cookies.
        :param int port: (optional) Custom port number for StoreOnce device.
        :return: None.
        """
        self._address = address
        self._user = user
        self._password = password
        self._cookie_dir = cookie_dir
        self._port = port

        # Default timeouts:
        # ConnectionTimeout = 1 second
        # ReadTimeout = infinity
        self._timeout = (1.0, None)

    @property
    def cookie_path(self):
        """
        Generate cookie file path.

        :rtype: str
        :return: Cookie file path
        """
        if not hasattr(self, '_cookie_path'):
            directory = self._cookie_dir or '.'
            filename = f'{self._address}.cookie'
            self._cookie_path = normpath(join(directory, filename))

        return self._cookie_path

    def _get_cookie_auth(self):
        if not hasattr(self, '_cookie_auth'):
            return requests.cookies.RequestsCookieJar()

        return self._cookie_auth

    def _set_cookie_auth(self, cookie=None):
        if cookie is not None:
            self._cookie_auth = cookie

    cookie_auth = property(_get_cookie_auth, _set_cookie_auth)

    @property
    def base_url(self):
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        return f'https://{self._address}:{self._port}'

    def __del__(self):
        if len(self.cookie_auth):
            save_cookie(self.cookie_path, self.cookie_auth)

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<class hpestorapi.{class_name}(address={self._address})>'

    def query(self, url, method, **kwargs):
        # Filter allowed kwargs to option dict
        allowed = ['params',
                   'data',
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
                           'Content-Type': 'application/x-www-form-urlencoded'}
        if 'headers' in option.keys():
            headers_default.update(option['headers'])
        option['headers'] = headers_default
        LOG.debug('headers=', option['headers'])

        # Add auth cookie for all requests
        if 'cookies' not in option.keys():
            option['cookies'] = requests.cookies.RequestsCookieJar()
        option['cookies'].update(self.cookie_auth)

        # By default SSL cert checking is disabled
        certcheck = kwargs.get('verify', False)

        # Set connection and read timeout (if not set by user)
        timeout = kwargs.pop('timeout', self.timeout)

        namespace = kwargs.pop('namespace', 'storeonceservices')

        # Prepare request
        path = '%s/%s/%s/' % (self.base_url, namespace.strip('/'), f'{url}'.strip('/'))
        session = requests.Session()
        request = requests.Request(method, path, **option)
        prepped = session.prepare_request(request)
        resp = requests.Response()
        LOG.debug('%s("%s", timeouts=%s)', method, path, timeout)
        LOG.debug('cookies=%s', option['cookies'])

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
                if self.open(use_cookie_file=False):
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
        filter = kwargs.get('filter', False)
        if filter:
            url = '%s?%s' % (url.strip('/'), filter)

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

    def open(self, use_cookie_file=True):
        """
        Perform HTTP PUT request to HPE Storeonce disk backup device. Method
        used to update objects.

        :param str url: URL address. Base part of url address is generated
            automatically and you should not care about it. Example of valid
            url: 'cluster' or 'cluster/servicesets'. All available url's
            and requests result are described in "HPE StoreOnce 3.18.2 REST
            API developer Guide"
        :param bool use_cookie_file: (optional) Try to load cookies from file.
        :param int timeout: (optional)
        :rtype: (int, string)
        :return: Tuple with HTTP status code and xml string with request
            result. For example: (200, '<xml> ... </xml>').
        """
        if use_cookie_file:
            self.cookie_auth = load_cookie(self.cookie_path)
            if len(self.cookie_auth):
                return True

        resp = self.query('/cluster', 'GET', auth=(self._user, self._password))
        if resp.status_code == requests.codes.ok:
            self._cookie_auth = resp.cookies
            LOG.debug('Authentification success')
            return True

        LOG.fatal('Cant authentificate on storeonce appliance')
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

    def _set_timeout(self, timeout):
        if isinstance(timeout, (float, int)):
            self._timeout = (timeout, timeout)
        elif isinstance(timeout, tuple):
            self._timeout = timeout

    def _get_timeout(self):
        return self._timeout

    def filter(self, url, parameters, **kwargs):
        """
        Get cookies for query with filtering

        :param str url: Filter URL address.
        :rtype: requests.cookies.RequestsCookieJar()
        :return: Filtering cookie
        """
        resp = self.query(url, 'POST', data=parameters, **kwargs)
        if resp.status_code == requests.codes.no_content:
            return resp.cookies

        LOG.critical('Cannot get filter cookie. Wrong device answer.')
        return None


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
    def __init__(self, device, url, items, filter=None):
        self.device = device
        self.url = url
        self.items = items
        self.filter = filter

        # Data page content
        self.page = None

        # Current element index on the data page
        self.index = 0

        # Is there any pages after current
        self.last = True

    def __next__(self):
        if self.page is None:
            # Request first data page
            resp = self.device.query(self.url, 'GET', cookies=self.cookies)
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

    def _get_cookies(self):
        if not hasattr(self, '_cookies'):
            return self.filter or requests.cookies.RequestsCookieJar()

        return self._cookies

    def _set_cookies(self, cookie):
        filter = self.filter or requests.cookies.RequestsCookieJar()
        self._cookies = requests.cookies.merge_cookies(filter, cookie)
        return self._cookies

    cookies = property(_get_cookies, _set_cookies)
