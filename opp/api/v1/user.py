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

from opp.api.v1 import base_handler as bh
from opp.common import aescipher, utils
from opp.db import api, models


class ResponseHandler(bh.BaseResponseHandler):
    """
    Response handler for the `user` endpoint.
    """

    def _validate(self, obj, name):
        """
        Validate the input object.

        :param obj: input object
        :param name: input object name

        :returns validated object or raises an error
        """
        obj = obj.strip()
        if not obj:
            raise bh.OppError("Input '%s' parameter is empty!" % name)

        return obj

    def _do_put(self, phrase):
        """
        Create a new user.

        :param phrase: not used

        :returns: success result
        """
        payload_dicts = [{'name': "username",
                          'is_list': False,
                          'required': True},
                         {'name': "password",
                          'is_list': False,
                          'required': True},
                         {'name': "phrase",
                          'is_list': False}]
        payload_objects = self._check_payload(payload_dicts)

        u = self._validate(payload_objects[0], 'username')
        p = self._validate(payload_objects[1], 'password')
        phrase = self._validate(payload_objects[2], 'phrase')
        if len(phrase) < 6:
            raise bh.OppError("Passphrase must be at least 6 characters long!")

        try:
            cipher = aescipher.AESCipher(phrase)
            ok = cipher.encrypt("OK")
            user = api.user_get_by_username(self.session, u)
            if user:
                raise bh.OppError("User already exists!")
            hashed = utils.hashpw(p)
            user = models.User(username=u, password=hashed, phrase_check=ok)
            api.user_create(self.session, user)
            user = api.user_get_by_username(self.session, u)
            if user:
                return {'result': 'success'}
            else:
                raise bh.OppError("Unable to add user: '%s'" % u)
        except bh.OppError as e:
            raise bh.OppError(e.error, e.desc, e.status, e.headers)
        except Exception:
            raise bh.OppError("Unable to add user: '%s'" % u)

    def _do_post(self, phrase):
        """
        Update a user.

        :param phrase: not used

        :returns: success result
        """
        payload_dicts = [{'name': "username",
                          'is_list': False,
                          'required': True},
                         {'name': "password",
                          'is_list': False,
                          'required': True},
                         {'name': "new_username",
                          'is_list': False,
                          'required': False},
                         {'name': "new_password",
                          'is_list': False,
                          'required': False}]
        payload_objects = self._check_payload(payload_dicts)

        u = self._validate(payload_objects[0], 'username')
        p = self._validate(payload_objects[1], 'password')
        new_u = payload_objects[2].strip()
        new_p = payload_objects[3].strip()
        if not(new_u or new_p):
            raise bh.OppError("at least one of: "
                              "[--new_username, --new_password] is required!")

        try:
            user = api.user_get_by_username(self.session, u)
            if not user:
                raise bh.OppError("User does not exist!")
            if not utils.checkpw(p, user.password):
                raise bh.OppError("Incorrect password supplied!")

            if new_u:
                new_user = api.user_get_by_username(self.session, new_u)
                if new_user:
                    raise bh.OppError("Username: '%s' already exists!" % new_u)

            if new_u:
                user.username = new_u
            if new_p:
                user.password = utils.hashpw(new_p)

            api.user_update(self.session, user)
            user = api.user_get_by_username(self.session, user.username)
            if user:
                return {'result': 'success'}
            else:
                raise bh.OppError("Unable to add user: '%s'" % u)
        except bh.OppError as e:
            raise bh.OppError(e.error, e.desc, e.status, e.headers)
        except Exception:
            raise bh.OppError("Unable to update user: '%s'" % u)

    def _do_delete(self):
        """
        Delete a user.

        :returns: success result
        """
        payload_dicts = [{'name': "username",
                          'is_list': False,
                          'required': True},
                         {'name': "password",
                          'is_list': False,
                          'required': True}]
        payload_objects = self._check_payload(payload_dicts)

        u = self._validate(payload_objects[0], 'username')
        p = self._validate(payload_objects[1], 'password')

        try:
            user = api.user_get_by_username(self.session, u)
            if not user:
                raise bh.OppError("User does not exist!")
            if not utils.checkpw(p, user.password):
                raise bh.OppError("Incorrect password supplied!")

            api.category_delete_all(self.session, user, True)
            api.item_delete_all(self.session, user)
            api.user_delete(self.session, user)

            user = api.user_get_by_username(self.session, u)
            if user:
                bh.OppError("Unable to delete user: '%s'" % u)
            else:
                return {'result': 'success'}
        except bh.OppError as e:
            raise bh.OppError(e.error, e.desc, e.status, e.headers)
        except Exception:
            raise bh.OppError("Unable to delate user: '%s'" % u)
