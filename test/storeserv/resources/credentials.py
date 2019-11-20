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

import flask
from flask_restful import Resource, reqparse


class Credentials(Resource):
    def __init__(self):
        self.auth = {'user': 'password'}
        self.key = '48A70B8A8301C458037E0821'

    def post(self, key=None):
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('Content-Type', type=str, location='headers',
                            choices='application/json', required=True)
        parser.add_argument('user', type=str, location='json', required=True)
        parser.add_argument('password', type=str, location='json',
                            required=True)
        arg = parser.parse_args()

        # Check credentials
        user = arg['user']
        password = arg['password']
        if (user in self.auth.keys()) and (password == self.auth.get(user)):
            return {'key': self.key}, 201

        return {'desc': 'Wrong username or password'}, 403

    def delete(self, key):
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('Content-Type', type=str, location='headers',
                            choices='application/json', required=True)
        parser.add_argument('X-HP3PAR-WSAPI-SessionKey', type=str,
                            location='headers', required=True)
        arg = parser.parse_args()

        # Check session key
        if key == self.key:
            return flask.Response(status=200)

        return flask.Response(status=403)
