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

"""Init module for hpestorapi library."""

# Remove flake8 warnings "imported but unused"
# flake8: noqa: F401

from .storeserv import StoreServ
from .storeonce3 import StoreOnceG3
from .storeonce4 import StoreOnceG4
from .xp import Xp
from .xp import CommandViewAE
from .primera import Primera


#  Semantic version number. Format: <MAJOR>.<MINOR>.<PATCH>
__version__ = '1.0.0'
