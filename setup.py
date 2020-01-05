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
.. moduleauthor:: Ivan Smirnov <ivan.smirnov@hpe.com>, HPE Pointnext DACH & Russia
"""

import os
from setuptools import setup

ROOT_DIR = os.path.dirname(__file__)

VERSION = '0.9.6'

setup(
    name='hpestorapi',
    version=VERSION,
    packages=['hpestorapi'],
    url='https://github.com/HewlettPackard/python-storage-clients',
    license='Apache License 2.0',
    author='Hewlett Packard Enterprise Development',
    author_email='ivan.smirnov@hpe.com',
    description=('Python library that provides very simple way to use '
                 'Rest API services for HPE storage and disk backup '
                 'devices'),
    long_description=open(os.path.join(ROOT_DIR, 'README.rst')).read(),
    long_description_content_type='text/x-rst',
    python_requires='>=3.6',
    install_requires=['requests>=2.19.1'],
    keywords=['HPE', 'REST', 'StoreOnce', '3PAR', 'Primera', 'XP7', 'Command View AE', 'Disk array'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
