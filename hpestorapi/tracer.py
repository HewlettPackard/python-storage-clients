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

"""Module with call tracer."""

from functools import wraps
import logging

logging.getLogger('hpestorapi').addHandler(logging.NullHandler())
LOG = logging.getLogger('hpestorapi')


def tracer(func):
    """Call tracer for functions and methods."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        params = ', '.join(map(str, args))

        if len(kwargs):
            params += ', '
            params += ', '.join(f'{k}="{v}"' for k, v in kwargs.items())

        LOG.debug(f'{func.__name__}({params})')
        return func(*args, **kwargs)
    return wrapper
