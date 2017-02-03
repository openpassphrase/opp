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

from opp.api.v1 import base_handler
from opp.db import api, models
from opp.common import aescipher


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        try:
            categories = api.category_getall(self.session, self.user)
            for category in categories:
                response.append(category.extract(cipher))
        except Exception:
            return self.error("Unable to fetch categories from the database!")
        return {'result': "success", 'categories': response}

    def _do_put(self, phrase):
        payload_dicts = [{'name': "category_names",
                          'is_list': True,
                          'required': True}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error
        cat_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Check for empty category name
            if not cat:
                return self.error("Empty category name in list!")
            try:
                blob = cipher.encrypt(cat)
                categories.append(models.Category(name=blob, user=self.user))
            except TypeError:
                return self.error("Invalid category name in list!")

        try:
            categories = api.category_create(self.session, categories)
        except Exception:
            return self.error("Unable to add new categories to the database!")

        response = []
        for category in categories:
            response.append(category.extract(cipher))
        return {'result': "success", 'categories': response}

    def _do_post(self, phrase):
        payload_dicts = [{'name': "categories",
                          'is_list': True,
                          'required': True}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error
        cat_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Make sure category id is parsed from request
            try:
                cat_id = cat['id']
            except KeyError:
                return self.error("Missing category id in list!")
            if not cat_id:
                return self.error("Empty category id in list!")

            # Make sure category is parsed from request
            try:
                category = cat['name']
            except KeyError:
                return self.error("Missing category name in list!")
            if not category:
                return self.error("Empty category name in list!")

            try:
                blob = cipher.encrypt(category)
                categories.append(models.Category(id=cat_id, name=blob,
                                                  user=self.user))
            except TypeError:
                return self.error("Invalid category name in list!")

        try:
            api.category_update(self.session, categories)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update categories in the database!")

    def _do_delete(self):
        payload_dicts = [{'name': "ids",
                          'is_list': True,
                          'required': True},
                         {'name': "cascade",
                          'is_list': False,
                          'required': True}]
        payload_objects, error = self._check_payload(payload_dicts)
        if error:
            return error
        categories, cascade = payload_objects

        # Additional validation of input parameters
        if not categories:
            return self.error("Empty category id list!")
        if cascade is not True and cascade is not False:
            return self.error("Invalid cascade value!")

        try:
            api.category_delete_by_id(self.session, self.user,
                                      categories, cascade)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete categories from the database!")
