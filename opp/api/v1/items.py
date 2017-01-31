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

from opp.api.v1 import base_handler
from opp.common import aescipher
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _parse_or_set_empty(self, row, key):
        try:
            value = row[key]
        except KeyError:
            return ""
        if value is None:
            return ""
        return value

    def _chunk6(self, string):
        chunk = int(len(string) / 6)
        chunks = []
        for i in range(0, 5):
            chunks.append(string[chunk * i: chunk * (i + 1)])
        chunks.append(string[chunk * 5:])
        return chunks

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        items = api.item_getall(self.user)
        for item in items:
            response.append(item.extract(cipher))

        return {'result': 'success', 'items': response}

    def _do_put(self, phrase):
        item_list, error = self._check_payload(expect_list=True)
        if error:
            return error

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
            category_id = self._parse_or_set_empty(row, 'category_id')
            full_row = [name, url, account, username, password, blob]

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
            api.item_create(items)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new items to the database!")

    def _do_post(self, phrase):
        item_list, error = self._check_payload(expect_list=True)
        if error:
            return error

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
            category_id = self._parse_or_set_empty(row, 'category_id')
            full_row = [name, url, account, username, password, blob]

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
            api.item_update(items)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update items in the database!")

    def _do_delete(self):
        payload, error = self._check_payload(expect_list=True)
        if error:
            return error

        try:
            api.item_delete_by_id(self.user, payload)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete items from the database!")
