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
from opp.db import api, models
from opp.common import aescipher


class ResponseHandler(bh.BaseResponseHandler):
    """
    Response handler for the `categories` endpoint.
    """

    def _do_get(self, phrase):
        """
        Fetch all user's categories.

        :param phrase: decryption passphrase

        :returns: success result along with decrypted categories array
        """
        response = []
        cipher = aescipher.AESCipher(phrase)
        try:
            categories = api.category_getall(self.session, self.user)
            for category in categories:
                response.append(category.extract(cipher))
        except Exception:
            raise bh.OppError("Unable to fetch categories from the database!")
        return {'result': "success", 'categories': response}

    def _do_put(self, phrase):
        """
        Create a list of categories, given an array of names.

        :param phrase: decryption passphrase

        :returns: success result along with array of newly created categories
        """
        payload_dicts = [{'name': "category_names",
                          'is_list': True,
                          'required': True}]
        payload_objects = self._check_payload(payload_dicts)
        cat_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Check for empty category name
            if not cat:
                raise bh.OppError("Empty category name in list!")
            try:
                blob = cipher.encrypt(cat)
                categories.append(models.Category(name=blob, user=self.user))
            except TypeError:
                raise bh.OppError("Invalid category name in list!")

        try:
            categories = api.category_create(self.session, categories)
        except Exception:
            raise bh.OppError("Unable to add new categories to the database!")

        response = []
        for category in categories:
            response.append(category.extract(cipher))
        return {'result': "success", 'categories': response}

    def _do_post(self, phrase):
        """
        Update a list of category names, identified by id.

        :param phrase: decryption passphrase

        :returns: success result
        """
        payload_dicts = [{'name': "categories",
                          'is_list': True,
                          'required': True}]
        payload_objects = self._check_payload(payload_dicts)
        cat_list = payload_objects[0]

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Make sure category id is parsed from request
            try:
                cat_id = cat['id']
            except KeyError:
                raise bh.OppError("Missing category id in list!")
            if not cat_id:
                raise bh.OppError("Empty category id in list!")

            # Make sure category is parsed from request
            try:
                category = cat['name']
            except KeyError:
                raise bh.OppError("Missing category name in list!")
            if not category:
                raise bh.OppError("Empty category name in list!")

            try:
                blob = cipher.encrypt(category)
                categories.append(models.Category(id=cat_id, name=blob,
                                                  user=self.user))
            except TypeError:
                raise bh.OppError("Invalid category name in list!")

        try:
            api.category_update(self.session, categories)
            return {'result': "success"}
        except Exception:
            raise bh.OppError("Unable to update categories in the database!")

    def _do_delete(self):
        """
        Delete a list of categories, identified by id, with optional `cascade`.
        specifier to proprage deletion of items belonging to the deleted
        categories.

        :returns: success result
        """
        payload_dicts = [{'name': "ids",
                          'is_list': True,
                          'required': True},
                         {'name': "cascade",
                          'is_list': False,
                          'required': True}]
        payload_objects = self._check_payload(payload_dicts)
        categories, cascade = payload_objects

        # Additional validation of input parameters
        if not categories:
            raise bh.OppError("Empty category id list!")
        if cascade is not True and cascade is not False:
            raise bh.OppError("Invalid cascade value!")

        try:
            api.category_delete_by_id(self.session, self.user,
                                      categories, cascade)
            return {'result': "success"}
        except Exception:
            raise bh.OppError("Unable to delete categories from the database!")
