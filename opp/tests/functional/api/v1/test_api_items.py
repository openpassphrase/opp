import json
import os
import tempfile
import unittest

from opp.api import v1 as api
from opp.common import utils


class TestBackendApiItems(unittest.TestCase):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        cls.connection = ("sql_connect: 'sqlite:///%s'" % cls.db_filepath)
        with open(cls.conf_filepath, 'wb') as conf_file:
            conf_file.write(cls.connection)
            conf_file.flush()
        os.environ['OPP_TOP_CONFIG'] = cls.conf_filepath
        utils.execute("opp-db --config_file %s init" % cls.conf_filepath)

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove(cls.conf_filepath)
        except Exception:
            pass
        try:
            os.remove(cls.db_filepath)
        except Exception:
            pass
        try:
            os.rmdir(cls.test_dir)
        except Exception:
            pass

    def setUp(self):
        # Create a test client
        self.client = api.app.test_client()
        # propagate exceptions to the test client
        self.client.testing = True

    def tearDown(self):
        pass

    def test_disallowed_methods_items(self):
        rpat = self.client.patch('/api/v1/items')
        self.assertEqual(rpat.status_code, 405)

    def test_items_crud(self):
        path = '/api/v1/items'
        headers = {'x-opp-phrase': "123"}

        # Request getall items, expect empty list initially
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

        # Add 3 items, check for successful response
        data = {'payload':
                '[{"name": "i1"}, {"name": "i2"}, {"name": "i3"}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 items
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 3)
        item1, item2, item3 = data['items']
        self.assertEqual(item1['name'], "i1")
        self.assertEqual(item2['name'], "i2")
        self.assertEqual(item3['name'], "i3")

        # Update items 1 & 3
        payload = [{'id': 1, 'name': "new_i1"},
                   {'id': 3, 'name': "new_i3"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 items again
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 3)
        item1, item2, item3 = data['items']
        self.assertEqual(item1['name'], "new_i1")
        self.assertEqual(item2['name'], "i2")
        self.assertEqual(item3['name'], "new_i3")

        # Delete items 1 & 3
        payload = [item1['id'], item3['id']]
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Get all items, only 1 sould remain
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i2")

        # Clean up by deleting item 2
        payload = [item2['id']]
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])

    def test_items_error_conditions(self):
        path = '/api/v1/items'
        headers = {'x-opp-phrase': "123"}

        # Try to PUT with missing item in list
        # data = {'payload': '[{}]'}
        # response = self.client.put(path, headers=headers, data=data)
        # self.assertEqual(response.status_code, 200)
        # data = json.loads(response.data)
        # self.assertEqual(data['result'], "error")
        # self.assertEqual(data['message'], "Missing item data in list!")

        # Try to PUT with empty item in list
        # data = {'payload': '[{"item": ""}]'}
        # response = self.client.put(path, headers=headers, data=data)
        # self.assertEqual(response.status_code, 200)
        # data = json.loads(response.data)
        # self.assertEqual(data['result'], "error")
        # self.assertEqual(data['message'], "Empty item data in list!")

        # Try to PUT with invalid item in list (int instead of string)
        data = {'payload': '[{"name": 2}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid item data in list!")

        # Add an item
        data = {'payload': '[{"name": "i4"}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Retrieve all items, expect only the one that was just added
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['name'], "i4")
        item_id = data['items'][0]['id']

        # Try to POST with missing item id
        payload = [{'noid': item_id}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing item id in list!")

        # Try to POST with empty item id
        payload = [{'id': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty item id in list!")

        # Try to POST with missing item
        # payload = [{'id': item_id, 'noitem': "new_i4"}]
        # data = {'payload': json.dumps(payload)}
        # response = self.client.post(path, headers=headers, data=data)
        # self.assertEqual(response.status_code, 200)
        # data = json.loads(response.data)
        # self.assertEqual(data['result'], "error")
        # self.assertEqual(data['message'], "Missing item in list!")

        # Try to POST with empty item
        # payload = [{'id': item_id, 'item': ""}]
        # data = {'payload': json.dumps(payload)}
        # response = self.client.post(path, headers=headers, data=data)
        # self.assertEqual(response.status_code, 200)
        # data = json.loads(response.data)
        # self.assertEqual(data['result'], "error")
        # self.assertEqual(data['message'], "Empty item in list!")

        # Try to POST with invalid item in list
        payload = [{'id': item_id, 'name': 1}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid item data in list!")

        # Clean up by deleting the item
        data = {'payload': json.dumps([item_id])}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall items, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['items'], [])
