#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP
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
.. module:: hpestorapi.primera
    :synopsis: Module with HPE Primera disk array wrapper

.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

import logging

from hpestorapi import StoreServ

if __name__ == "__main__":
    pass

LOG = logging.getLogger('hpestorapi.primera')


class Primera(StoreServ):
    """
        HPE Primera array implementation class.
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

        # Device port number (default WSAPI port is 443)
        port = self._port or 443

        return f'{proto}://{self._address}:{port}/api/v1'
