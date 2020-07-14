#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   (C) Copyright 2020 Hewlett Packard Enterprise Development LP
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

"""Module with HPE StoreOnce Gen3 disk backup device additional utilities."""

import logging
from os.path import isfile
import pickle

from hpestorapi.base import tracer

logging.getLogger('hpestorapi.storeonce').addHandler(logging.NullHandler())
LOG = logging.getLogger('hpestorapi.storeonce')


@tracer
def load_cookie(filepath):
    """
    Load cookies from cookie file.

    :rtype: RequestsCookieJar|None
    :return: Returns cookies in case of success or None.
    """
    # Check file path
    if not isfile(filepath):
        LOG.info('Cant open cookie file. Filename = "%s"', filepath)
        return None

    # Check permissions and open cookie file
    try:
        fd = open(filepath, 'rb')
    except OSError as error:
        LOG.error('Cant open cookie file. Filename = "%s"', filepath)
        LOG.error(error)
        return None

    # Load cookie from file
    with fd:
        try:
            cookie = pickle.load(fd)
        except pickle.UnpicklingError:
            LOG.error('Cannot load cookies from cookie file. Broken file '
                      'format. Filename = "%s"', filepath)
            return None
        else:
            LOG.debug('Auth cookie succefully loaded from file.')

        # Cookie file has at least one record
        if cookie:
            return cookie

    return None


@tracer
def save_cookie(filepath, cookie):
    """
    Dump cookies to file.

    :rtype: bool
    :return: True if successfully saved. In other cases returns False.
    """
    # Truncate cookies file
    try:
        fd = open(filepath, 'wb')
        fd.truncate()
    except OSError as error:
        LOG.error('Can not write to cookie file. Filename = "%s"', filepath)
        LOG.error(error)
        return False

    # Save cookies to file
    with fd:
        try:
            pickle.dump(cookie, fd)
        except pickle.PicklingError as error:
            LOG.error('Can not save cookies to file.')
            LOG.error(error)
            return False

    LOG.debug('Cookie successfully saved to file.')
    return True
