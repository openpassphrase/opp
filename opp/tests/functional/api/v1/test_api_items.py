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
        self.hdrs = {'x-opp-phrase': "123456",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Request getall items, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

        # Add 3 items, check for successful response
        data = {'items':
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
        items = [{'id': 1, 'name': "new_i1"},
                 {'id': 3, 'name': "new_i3"}]
        data = {'items': items}
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
        data = {'ids': [item1['id'], item3['id']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Get all items, only 1 sould remain
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i2")

        # Clean up by deleting item 2
        data = {'ids': [item2['id']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

    def test_items_error_conditions(self):
        self.hdrs = {'x-opp-phrase': "123456",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Try to PUT with invalid item in list (int instead of string)
        data = {'items': [{"name": 2}]}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'], "Invalid item data in list!")

        # Add an item
        data = {'items': [{"name": "i4"}]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Retrieve all items, expect only the one that was just added
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i4")
        item_id = data['items'][0]['id']

        # Try to POST with missing item id
        data = {'items': [{'noid': item_id}]}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Missing item id in list!")

        # Try to POST with empty item id
        data = {'items': [{'id': ""}]}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Empty item id in list!")

        # Try to POST with invalid item in list
        data = {'items': [{'id': item_id, 'name': 1}]}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Invalid item data in list!")

        # Clean up by deleting the item
        data = {'ids': [item_id]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

    def test_items_create_auto_password(self):
        self.hdrs = {'x-opp-phrase': "123456",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Request getall items, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

        # Add 2 items with autogenerate password option
        data = {'items':
                [{"name": "i1"}, {"name": "i2"}],
                'auto_pass': True}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Check item passwords
        self.assertEqual(len(data['items']), 2)
        item1, item2 = data['items']
        self.assertEqual(item1['name'], "i1")
        self.assertEqual(item2['name'], "i2")
        self.assertEqual(item1['password'], item2['password'])
        self.assertEqual(len(item1['password'].split(" ")), 6)

        # Add 2 items with autogenerate password and unique options
        data = {'items':
                [{"name": "i3"}, {"name": "i4"}],
                'auto_pass': True, 'unique': True,
                'genopts': {'numwords': 10, 'delimiter': "~"}}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Check item passwords
        self.assertEqual(len(data['items']), 2)
        item1, item2 = data['items']
        self.assertEqual(item1['name'], "i3")
        self.assertEqual(item2['name'], "i4")
        self.assertNotEqual(item1['password'], item2['password'])
        self.assertEqual(len(item1['password'].split("~")), 10)
        self.assertEqual(len(item2['password'].split("~")), 10)

        # Clean up
        data = self._get(path)
        data = {'ids': [item['id'] for item in data['items']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

    def test_items_update_auto_password(self):
        self.hdrs = {'x-opp-phrase': "123456",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/items'

        # Request getall items, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

        # Add 2 items with passwords
        data = {'items':
                [{"password": "p1"}, {"password": "p2"}]}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Check item passwords
        self.assertEqual(len(data['items']), 2)
        item1, item2 = data['items']
        self.assertEqual(item1['password'], "p1")
        self.assertEqual(item2['password'], "p2")

        # Update items with autogenerate password option
        data = {'items':
                [{"id": item1['id']}, {"id": item2['id']}],
                'auto_pass': True}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Check item passwords
        data = self._get(path)
        self.assertEqual(len(data['items']), 2)
        item1, item2 = data['items']
        self.assertEqual(item1['password'], item2['password'])
        self.assertEqual(len(item1['password'].split(" ")), 6)

        # Update items with autogenerate password and unique options
        data = {'items':
                [{"id": item1['id']}, {"id": item2['id']}],
                'auto_pass': True, 'unique': True,
                'genopts': {'numwords': 10, 'delimiter': "~"}}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Check item passwords
        data = self._get(path)
        self.assertEqual(len(data['items']), 2)
        item1, item2 = data['items']
        self.assertNotEqual(item1['password'], item2['password'])
        self.assertEqual(len(item1['password'].split("~")), 10)
        self.assertEqual(len(item2['password'].split("~")), 10)

        # Clean up
        data = self._get(path)
        data = {'ids': [item['id'] for item in data['items']]}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")
