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
    """
    This a base class implementing functionality common
    to all response handlers derived from it.
    """

    def __init__(self, request, user, session):
        # Request data
        self.request = request
        # User context
        self.user = user
        # SQLAlchemy scoped session
        self.session = session

    def _check_payload(self, check_dict=None):
        """
        This function checks the JSON payload for presence of objects
        specified in the check_dict array.

        :param check_dict: an array of items where each item contains the
        name of the JSON object to search for, whether or not it is required
        to be present, and whether it is a regular JSON object or a JSON array.

        :returns: a list of objects extracted from the payload, in the same
        order as specified in check_dict array.
        """
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
        """This is the HTTP GET handler implemented in the derived class."""
        raise OppError("Action not implemented")

    def _do_put(self, phrase):
        """This is the HTTP PUT handler implemented in the derived class."""
        raise OppError("Action not implemented")

    def _do_post(self, phrase):
        """This is the HTTP POST handler implemented in the derived class."""
        raise OppError("Action not implemented")

    def _do_delete(self):
        """This is the HTTP DELETE handler implemented in the derived class."""
        raise OppError("Action not implemented")

    def respond(self, require_phrase=True):
        """
            This is the main function called by the request processing logic
            to generate a response for a particular endpoint call.
        """
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
    """Generic error class for propagating HTTP error codes and messages."""
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
