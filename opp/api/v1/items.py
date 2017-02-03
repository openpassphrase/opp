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

import base64

from xkcdpass import xkcd_password as xp

from opp.api.v1 import base_handler
from opp.common import aescipher
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _parse_or_set_empty(self, row, key, none_if_empty=False):
        try:
            value = row[key]
        except KeyError:
            if none_if_empty:
                return None
            else:
                return ""
        if not none_if_empty and value is None:
            return ""
        return value

    def _chunk6(self, string):
        chunk = int(len(string) / 6)
        chunks = []
        for i in range(0, 5):
            chunks.append(string[chunk * i: chunk * (i + 1)])
        chunks.append(string[chunk * 5:])
        return chunks

    def _genpwd(self, count, options):
        wordfile = xp.locate_wordfile()

        try:
            min_length = options['min_length']
        except (TypeError, KeyError):
            min_length = 5
        try:
            max_length = options['max_length']
        except (TypeError, KeyError):
            max_length = 9
        try:
            valid_chars = options['valid_chars']
        except (TypeError, KeyError):
            valid_chars = "."
        try:
            numwords = options['numwords']
        except (TypeError, KeyError):
            numwords = 6
        try:
            delimiter = options['delimiter']
        except (TypeError, KeyError):
            delimiter = " "

        mywords = xp.generate_wordlist(wordfile=wordfile,
                                       min_length=min_length,
                                       max_length=max_length,
                                       valid_chars=valid_chars)
        for x in range(count):
            yield xp.generate_xkcdpassword(mywords,
                                           numwords=numwords,
                                           interactive=False,
                                           acrostic=False,
                                           delimiter=delimiter)

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        try:
            items = api.item_getall(self.session, self.user)
            for item in items:
                response.append(item.extract(cipher))
        except Exception:
            return self.error("Unable to fetch items from the database!")
        return {'result': 'success', 'items': response}

    def _do_put(self, phrase):
        payload_dicts = [{'name': "items",
                          'is_list': True,
                          'required': True},
                         {'name': "autogenerate",
                          'is_list': False,
                          'required': False}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error
        item_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            # Extract various item data into a list
            name = self._parse_or_set_empty(row, 'name')
            url = self._parse_or_set_empty(row, 'url')
            account = self._parse_or_set_empty(row, 'account')
            username = self._parse_or_set_empty(row, 'username')
            password = self._parse_or_set_empty(row, 'password')
            blob = self._parse_or_set_empty(row, 'blob')
            full_row = [name, url, account, username, password, blob]

            category_id = self._parse_or_set_empty(row, 'category_id', True)

            try:
                # TODO: (alex) deteremine if ok to insert completely empty item
                encoded_row = [base64.b64encode(x.encode()).decode() for
                               x in full_row]
                encrypted_blob = cipher.encrypt("~".join(encoded_row))
                [name, url, account, username, password, blob] = self._chunk6(
                    encrypted_blob.decode())
                items.append(models.Item(name=name, url=url, account=account,
                                         username=username, password=password,
                                         blob=blob, category_id=category_id,
                                         user=self.user))
            except (AttributeError, TypeError):
                return self.error("Invalid item data in list!")

        try:
            items = api.item_create(self.session, items)
        except Exception:
            return self.error("Unable to add new items to the database!")

        response = []
        for item in items:
            response.append(item.extract(cipher))
        return {'result': 'success', 'items': response}

    def _do_post(self, phrase):
        payload_dicts = [{'name': "items",
                          'is_list': True,
                          'required': True},
                         {'name': "autogenerate",
                          'is_list': False,
                          'required': False}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error
        item_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            # Make sure item id is parsed from request
            try:
                item_id = row['id']
            except KeyError:
                return self.error("Missing item id in list!")
            if not item_id:
                return self.error("Empty item id in list!")

            # Extract various item data into a list
            name = self._parse_or_set_empty(row, 'name')
            url = self._parse_or_set_empty(row, 'url')
            account = self._parse_or_set_empty(row, 'account')
            username = self._parse_or_set_empty(row, 'username')
            password = self._parse_or_set_empty(row, 'password')
            blob = self._parse_or_set_empty(row, 'blob')
            full_row = [name, url, account, username, password, blob]

            category_id = self._parse_or_set_empty(row, 'category_id', True)

            try:
                # TODO: (alex) deteremine if ok to insert completely empty item
                encoded_row = [base64.b64encode(x.encode()).decode() for
                               x in full_row]
                encrypted_blob = cipher.encrypt("~".join(encoded_row))
                [name, url, account, username, password, blob] = self._chunk6(
                    encrypted_blob.decode())
                items.append(models.Item(id=item_id, name=name, url=url,
                                         account=account, username=username,
                                         password=password, blob=blob,
                                         category_id=category_id,
                                         user=self.user))
            except (AttributeError, TypeError):
                return self.error("Invalid item data in list!")

        try:
            api.item_update(self.session, items)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update items in the database!")

    def _do_delete(self):
        payload_dicts = [{'name': "ids",
                          'is_list': True,
                          'required': True}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error

        id_list = payload_objects[0]

        try:
            api.item_delete_by_id(self.session, self.user, id_list)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete items from the database!")
