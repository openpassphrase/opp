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

from . import BackendApiTest


class TestCase(BackendApiTest):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""

    def test_disallowed_methods_categories(self):
        rpat = self.client.patch('/v1/categories')
        self.assertEqual(rpat.status_code, 405)

    def test_categories_crud(self):
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/categories'

        # Request getall categories, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add 3 categories, check for successful response
        data = {'payload': ["cat1", "cat2", "cat3"]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Check all 3 categories
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 3)
        cat1, cat2, cat3 = data['categories']
        self.assertEqual(cat1['name'], "cat1")
        self.assertEqual(cat2['name'], "cat2")
        self.assertEqual(cat3['name'], "cat3")

        # Update categories 1 & 3
        payload = [{'id': 1, 'name': "new_cat1"},
                   {'id': 3, 'name': "new_cat3"}]
        data = {'payload': payload}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Check all 3 categories
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 3)
        cat1, cat2, cat3 = data['categories']
        self.assertEqual(cat1['name'], "new_cat1")
        self.assertEqual(cat2['name'], "cat2")
        self.assertEqual(cat3['name'], "new_cat3")

        # Delete categories 1 & 3
        payload = {'cascade': False, 'ids': [cat1['id'], cat3['id']]}
        data = {'payload': payload}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Get all categories, only 1 sould remain
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], "cat2")

        # Clean up by deleting category 2
        payload = {'cascade': False, 'ids': [cat2['id']]}
        data = {'payload': payload}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

    def test_categories_error_conditions(self):
        path = '/v1/categories'
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}

        # Try to PUT with empty category list
        data = {'payload': ["cat1", ""]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category name in list!")

        # Try to PUT with invalid category name in list (int instead of string)
        data = {'payload': ["cat1", 2]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category name in list!")

        # Add a category
        data = {'payload': ["cat4"]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Retrieve all categories, expect only the one that was just added
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], "cat4")
        cat_id = data['categories'][0]['id']

        # Try to POST with missing category id
        data = {'payload': [{'noid': cat_id}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id in list!")

        # Try to POST with empty category id
        data = {'payload': [{'id': ""}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id in list!")

        # Try to POST with missing category name
        data = {'payload': [{'id': cat_id, 'nocategory': "new_cat4"}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category name in list!")

        # Try to POST with empty category name
        data = {'payload': [{'id': cat_id, 'name': ""}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category name in list!")

        # Try to POST with invalid category name in list
        data = {'payload': [{'id': cat_id, 'name': 1}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category name in list!")

        # Try to delete with invalid payload (list form)
        data = {'payload': [1, 2, 3]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'],
                         "Payload should not be in list form!")

        # Try to delete with missing cascade value
        data = {'payload': {'notcascade': False, 'ids': [2]}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing cascade value!")

        # Try to delete with invalid cascade value (string instead of boolean)
        data = {'payload': {'cascade': "False", 'ids': [2]}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid cascade value!")

        # Try to delete with missing category id list
        data = {'payload': {'cascade': False, 'notids': [2]}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id list!")

        # Try to delete with empty category id list
        data = {'payload': {'cascade': False, 'ids': []}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id list!")

        # Try to delete with invalid category id list
        data = {'payload': {'cascade': False, 'ids': "1"}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category id list!")

        # Clean up by deleting the category
        data = {'payload': {'cascade': False, 'ids': [cat_id]}}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

    def test_categories_delete_cascade(self):
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        cat_path = '/v1/categories'
        item_path = '/v1/items'

        # Request getall categories, expect empty list initially
        data = self._get(cat_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add two categories
        data = {'payload': ["cat1", "cat2"]}
        data = self._put(cat_path, data)
        self.assertEqual(data['result'], "success")

        # Verify new categories
        data = self._get(cat_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 2)
        c1, c2 = data['categories']

        # Add four items (two per category)
        items = [{'name': "i1", 'category_id': c1['id']},
                 {'name': "i2", 'category_id': c1['id']},
                 {'name': "i3", 'category_id': c2['id']},
                 {'name': "i4", 'category_id': c2['id']}]
        data = {'payload': items}
        data = self._put(item_path, data)
        self.assertEqual(data['result'], "success")

        # Verify new items
        data = self._get(item_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 4)

        i1, i2, i3, i4 = data['items']

        self.assertEqual(i1['name'], "i1")
        self.assertEqual(i1['category']['name'], c1['name'])
        self.assertEqual(i1['category']['id'], c1['id'])

        self.assertEqual(i2['name'], "i2")
        self.assertEqual(i2['category']['name'], c1['name'])
        self.assertEqual(i2['category']['id'], c1['id'])

        self.assertEqual(i3['name'], "i3")
        self.assertEqual(i3['category']['name'], c2['name'])
        self.assertEqual(i3['category']['id'], c2['id'])

        self.assertEqual(i4['name'], "i4")
        self.assertEqual(i4['category']['name'], c2['name'])
        self.assertEqual(i4['category']['id'], c2['id'])

        # Delete category 1 with cascade
        payload = {'cascade': True, 'ids': [c1['id']]}
        data = {'payload': payload}
        data = self._delete(cat_path, data)
        self.assertEqual(data['result'], "success")

        # Verify updated category list (expect 1)
        data = self._get(cat_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['id'], c2['id'])

        # Verify updated items list (expect 2)
        data = self._get(item_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 2)
        i3, i4 = data['items']
        self.assertEqual(i3['name'], "i3")
        self.assertEqual(i3['category']['name'], c2['name'])
        self.assertEqual(i3['category']['id'], c2['id'])
        self.assertEqual(i4['name'], "i4")
        self.assertEqual(i4['category']['name'], c2['name'])
        self.assertEqual(i4['category']['id'], c2['id'])

        # Delete category 2 without cascade
        payload = {'cascade': False, 'ids': [c2['id']]}
        data = {'payload': payload}
        data = self._delete(cat_path, data)
        self.assertEqual(data['result'], "success")

        # Verify empty category list
        data = self._get(cat_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 0)

        # Verify updated items list (expect 2 with no categories)
        data = self._get(item_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 2)
        i3, i4 = data['items']
        self.assertEqual(i3['name'], "i3")
        self.assertEqual(i3['category']['id'], None)
        self.assertEqual(i4['name'], "i4")
        self.assertEqual(i4['category']['id'], None)

        # Delete remaining two items to clean up
        data = {'payload': [i3['id'], i4['id']]}
        data = self._delete(item_path, data)
        self.assertEqual(data['result'], "success")

        data = self._get(item_path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 0)
