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
from random import randint
import json


class Credentials(Resource):
    def __init__(self):
        self.users = [{'3paradm': {'role': 'Super', 'password': '3pardata'}},
                      {'user': {'role': 'Browse', 'password': 'password'}}
                     ]
        self.sessions = self.load_sessions()

    def auth_check(self, user, password):
        """
        Check user credentials.

        :param user: Device username.
        :param password: Device password.
        :return: Role name (if authorized) or None.
        """
        role = None
        for record in self.users:
            if user in record.keys():
                if password == record.get(user).get('password'):
                    role = record.get(user).get('password')

        return role

    def __del__(self):
        self.save_sessions(self.sessions)

    def load_sessions(self):
        """
        Get sessions list from disk.

        :return: dict()
        """
        try:
            with open("sessions.json") as file:
                data = json.load(file)
        except:
            data = {}

        return data

    def save_sessions(self, data):
        """
         Dump sessions list to disk.

        :return: None
        """
        try:
            with open("sessions.json", "w") as file:
                json.dump(data, file)
        except:
            print("Can not save active sessions list to disk. Check permissions.")

    def gen_seskey(self):
        """
        Generate new 3PAR WSAPI session key.

        :return:
        """
        return ''.join([str(format(randint(0, 15), 'X')) for i in range(24)])

    def post(self, key=None):
        """
        Open new HPE 3PAR WSAPI session.
        """
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
        if self.auth_check(user, password) is not None:
            key = self.gen_seskey()
            self.sessions[key] = user
            return {'key': key}, 201

        return {'desc': 'Wrong username or password'}, 403

    def delete(self, key):
        """
        Close HPE 3PAR WSAPI session
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Content-Type', type=str, location='headers',
                            choices='application/json', required=True)
        parser.add_argument('X-HP3PAR-WSAPI-SessionKey', type=str,
                            location='headers', required=True)
        arg = parser.parse_args()

        # Check session key
        if key in self.sessions.keys():
            self.sessions.pop(key)
            return flask.Response(status=200)

        return flask.Response(status=403)
