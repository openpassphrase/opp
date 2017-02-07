# Copyright 2017 OpenPassPhrase
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import OrderedDict
import json

from opp.common import aescipher


class BaseResponseHandler(object):

    def __init__(self, request, user, session):
        self.request = request
        self.user = user
        self.session = session

    def _check_payload(self, check_dict=None):
        request_body = self.request.get_json()
        payload_objects = []

        if not check_dict:
            return payload_objects
        elif not request_body:
            raise OppError("Missing payload!")

        for obj in check_dict:
            try:
                payload_obj = request_body[obj['name']]
                if obj['is_list']:
                    if not isinstance(payload_obj, list):
                        raise OppError("'%s' object should be in"
                                       " list form!" % obj['name'])
                else:
                    if isinstance(payload_obj, list):
                        raise OppError("'%s' object should not be "
                                       "in list form!" % obj['name'])
                payload_objects.append(payload_obj)
            except KeyError:
                if obj['required']:
                    raise OppError("Required payload object '%s'"
                                   " is missing!" % obj['name'])
                else:
                    if obj['is_list']:
                        payload_objects.append([])
                    else:
                        payload_objects.append({})

        return payload_objects

    def _do_get(self, phrase):
        raise OppError("Action not implemented")

    def _do_put(self, phrase):
        raise OppError("Action not implemented")

    def _do_post(self, phrase):
        raise OppError("Action not implemented")

    def _do_delete(self):
        raise OppError("Action not implemented")

    def respond(self, require_phrase=True):
        # Validate passphrase if required
        if require_phrase:
            try:
                phrase = self.request.headers['x-opp-phrase']
            except KeyError:
                raise OppError("Passphrase header missing!")

            cipher = aescipher.AESCipher(phrase)
            if cipher.decrypt(self.user.phrase_check) != "OK":
                raise OppError("Incorrect passphrase supplied!")
        else:
            phrase = None

        with self.session.begin():
            if self.request.method == "GET":
                response = self._do_get(phrase)
            elif self.request.method == "PUT":
                response = self._do_put(phrase)
            elif self.request.method == "POST":
                response = self._do_post(phrase)
            elif self.request.method == "DELETE":
                response = self._do_delete()
            else:
                raise OppError("Method not supported!")

        return response


class OppError(Exception):
    def __init__(self, error, desc=None, status=400, headers=None):
        self.error = error or ""
        self.desc = desc or ""
        self.status = status or 400
        self.headers = headers

    def __repr__(self):
        return 'OppError: %s' % self.error

    def __str__(self):
        return '%s. %s' % (self.error, self.desc)

    def json(self):
        dumps = OrderedDict([('status_code', self.status),
                             ('error', self.error),
                             ('description', self.desc)])
        return json.dumps(dumps, indent=4)
