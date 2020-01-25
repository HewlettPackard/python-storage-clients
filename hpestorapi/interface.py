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

"""
.. module:: hpestorapi.interface
    :synopsis: Abstract base interface for all devices

.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

from abc import ABC, abstractmethod


class BaseAPI(ABC):
    @abstractmethod
    def _base_url(self):
        """
        Generate static part of URL.

        :rtype: str
        :return: Static part of URL
        """
        raise NotImplementedError

    @abstractmethod
    def open(self):
        """
        Open Rest API session.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """
        Close Rest API session.

        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, url, **kwargs):
        """
        Perform HTTP GET request to device. Method used to get
        information about objects.

        :param str url: Relative URL address.
        """
        raise NotImplementedError