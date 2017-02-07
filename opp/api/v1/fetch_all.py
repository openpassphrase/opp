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
from opp.common import aescipher
from opp.db import api


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_get(self, phrase):
        cat_array = []
        item_array = []
        cipher = aescipher.AESCipher(phrase)
        try:
            categories = api.category_getall(self.session, self.user)
            for category in categories:
                cat_array.append(category.extract(cipher, with_items=False))

            items = api.item_getall(self.session, self.user)
            for item in items:
                item_array.append(item.extract(cipher, with_category=False))
        except Exception:
            return self.error("Unable to fetch from the database!")

        return {'result': 'success',
                'categories': cat_array,
                'items': item_array}
