#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   (C) Copyright 2017-2019 Hewlett Packard Enterprise Development LP
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
.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

from setuptools import setup

setup(
    name='hpestorapi',
    version='0.9.4',
    packages=['hpestorapi'],
    url='https://github.com/HewlettPackard/python-storage-clients',
    license=open('LICENSE.txt').read(),
    author='Hewlett Packard Enterprise Development',
    author_email='ivan.smirnov@hpe.com',
    description=('Python library that provides very simple way to use '
                 'Rest API services for HPE storage and disk backup '
                 'devices'),
    python_requires='>=3.6',
    install_requires=['requests']
)
