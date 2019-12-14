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

import json

from flask_restful import Resource, reqparse

from .common import response
from .credentials import Credentials


class System(Resource):
    def get(self):
        """
        Get general information about storage system.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Content-Type', type=str, location='headers',
                            choices='application/json', required=True)
        parser.add_argument('X-HP3PAR-WSAPI-SessionKey', type=str,
                            location='headers', required=True)
        arg = parser.parse_args()

        # Is session key active?
        auth = Credentials()
        if not auth.check_seskey(arg['X-HP3PAR-WSAPI-SessionKey']):
            return response(403)

        # Load response body from file
        with open('resources/system-get.json') as file:
            data = json.load(file)

        # Return flask response
        return response(200, data)
