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


class BaseResponseHandler(object):

    def __init__(self, request, user, session):
        self.request = request
        self.user = user
        self.session = session

    def error(self, msg=None):
        return {'result': "error", 'message': msg}

    def _check_payload(self, expect_list):
        request_body = self.request.get_json()

        try:
            payload = request_body['payload']
        except KeyError:
            return None, self.error("Payload missing!")

        if not payload:
            return None, self.error("Empty payload!")

        if expect_list:
            if not isinstance(payload, list):
                return None, self.error("Payload should be in list form!")
        else:
            if isinstance(payload, list):
                return None, self.error("Payload should not be in list form!")

        return payload, None

    def _do_get(self, phrase):
        return self.error("Action not implemented")

    def _do_put(self, phrase):
        return self.error("Action not implemented")

    def _do_post(self, phrase):
        return self.error("Action not implemented")

    def _do_delete(self):
        return self.error("Action not implemented")

    def respond(self, require_phrase=True):
        if require_phrase:
            try:
                phrase = self.request.headers['x-opp-phrase']
            except KeyError:
                return self.error("Passphrase header missing!")
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
                response = self.error("Method not supported!")

        return response


class ErrorResponseHandler(BaseResponseHandler):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return self.error(self.message)
