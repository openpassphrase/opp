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
    def test_disallowed_methods_items(self):
        rpat = self.client.patch('/v1/items')
        self.assertEqual(rpat.status_code, 405)

    def test_items_crud(self):
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Request getall items, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

        # Add 3 items, check for successful response
        data = {'payload':
                [{"name": "i1"}, {"name": "i2"}, {"name": "i3"}]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Check all 3 items
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 3)
        item1, item2, item3 = data['items']
        self.assertEqual(item1['name'], "i1")
        self.assertEqual(item2['name'], "i2")
        self.assertEqual(item3['name'], "i3")

        # Update items 1 & 3
        payload = [{'id': 1, 'name': "new_i1"},
                   {'id': 3, 'name': "new_i3"}]
        data = {'payload': payload}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Check all 3 items again
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 3)
        item1, item2, item3 = data['items']
        self.assertEqual(item1['name'], "new_i1")
        self.assertEqual(item2['name'], "i2")
        self.assertEqual(item3['name'], "new_i3")

        # Delete items 1 & 3
        data = {'payload': [item1['id'], item3['id']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Get all items, only 1 sould remain
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i2")

        # Clean up by deleting item 2
        payload = [item2['id']]
        data = {'payload': [item2['id']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

    def test_items_error_conditions(self):
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Try to PUT with invalid item in list (int instead of string)
        data = {'payload': [{"name": 2}]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid item data in list!")

        # Add an item
        data = {'payload': [{"name": "i4"}]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Retrieve all items, expect only the one that was just added
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i4")
        item_id = data['items'][0]['id']

        # Try to POST with missing item id
        data = {'payload': [{'noid': item_id}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing item id in list!")

        # Try to POST with empty item id
        data = {'payload': [{'id': ""}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty item id in list!")

        # Try to POST with invalid item in list
        data = {'payload': [{'id': item_id, 'name': 1}]}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid item data in list!")

        # Clean up by deleting the item
        data = {'payload': [item_id]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])
