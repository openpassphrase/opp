import json
import os
import tempfile
import unittest

from opp.api import v1 as api
from opp.common import utils


class BackendApiTests(unittest.TestCase):

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

    def test_health_check(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         '{"status": "OpenPassPhrase service is running"}')

    def test_disallowed_methods_categories(self):
        rpat = self.client.patch('/api/v1/categories')
        self.assertEqual(rpat.status_code, 405)

    def test_disallowed_methods_items(self):
        rpat = self.client.patch('/api/v1/items')
        self.assertEqual(rpat.status_code, 405)

    def test_categories_crud(self):
        path = '/api/v1/categories'
        headers = {'x-opp-phrase': "123"}

        # Request getall categories, expect empty list initially
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add 3 categories, check for successful response
        data = {'payload': '["cat1", "cat2", "cat3"]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Update categories 1 & 3
        payload = [{'id': 1, 'category': "new_cat1"},
                   {'id': 3, 'category': "new_cat3"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 categories
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 3)
        cat1, cat2, cat3 = data['categories']
        self.assertEqual(cat1['category'], "new_cat1")
        self.assertEqual(cat2['category'], "cat2")
        self.assertEqual(cat3['category'], "new_cat3")

        # Delete categories 1 & 3
        payload = {'cascade': False, 'ids': [cat1['id'], cat3['id']]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Get all categories, only 1 sould remain
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['category'], "cat2")

        # Clean up by deleting category 2
        payload = {'cascade': False, 'ids': [cat2['id']]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

    def test_categories_error_conditions(self):
        path = '/api/v1/categories'
        headers = {'x-opp-phrase': "123"}

        # Try to PUT with empty category list
        data = {'payload': '["cat1", ""]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category data in list!")

        # Try to PUT with invalid category in list (int instead of string)
        data = {'payload': '["cat1", 2]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category data in list!")

        # Add a category
        data = {'payload': '["cat4"]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Retrieve all categories, expect only the one that was just added
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['category'], "cat4")
        cat_id = data['categories'][0]['id']

        # Try to POST with missing category id
        payload = [{'noid': cat_id}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id in list!")

        # Try to POST with empty category id
        payload = [{'id': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id in list!")

        # Try to POST with missing category
        payload = [{'id': cat_id, 'nocategory': "new_cat4"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category in list!")

        # Try to POST with empty category
        payload = [{'id': cat_id, 'category': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category in list!")

        # Try to POST with invalid category in list
        payload = [{'id': cat_id, 'category': 1}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category data in list!")

        # Try to delete with invalid payload (list form)
        data = {'payload': '[1,2,3]'}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'],
                         "Payload should not be in list form!")

        # Try to delete with missing cascade value
        payload = {'notcascade': False, 'ids': [2]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing cascade value!")

        # Try to delete with invalid cascade value (string instead of boolean)
        payload = {'cascade': "False", 'ids': [2]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid cascade value!")

        # Try to delete with missing category id list
        payload = {'cascade': False, 'notids': [2]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id list!")

        # Try to delete with empty category id list
        payload = {'cascade': False, 'ids': []}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id list!")

        # Try to delete with invalid category id list
        payload = {'cascade': False, 'ids': "1"}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category id list!")

        # Clean up by deleting the category
        payload = {'cascade': False, 'ids': [cat_id]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

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
                '[{"item": "i1"}, {"item": "i2"}, {"item": "i3"}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Update items 1 & 3
        payload = [{'id': 1, 'item': "new_i1"},
                   {'id': 3, 'item': "new_i3"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
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
        self.assertEqual(item1['item'], "new_i1")
        self.assertEqual(item2['item'], "i2")
        self.assertEqual(item3['item'], "new_i3")

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
        self.assertEqual(data['items'][0]['item'], "i2")

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
        data = {'payload': '[{}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing item data in list!")

        # Try to PUT with empty item in list
        data = {'payload': '[{"item": ""}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty item data in list!")

        # Try to PUT with invalid item in list (int instead of string)
        data = {'payload': '[{"item": 2}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid item data in list!")

        # Add an item
        data = {'payload': '[{"item": "i4"}]'}
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
        self.assertEqual(data['items'][0]['item'], "i4")
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
        payload = [{'id': item_id, 'noitem': "new_i4"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing item in list!")

        # Try to POST with empty item
        payload = [{'id': item_id, 'item': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty item in list!")

        # Try to POST with invalid item in list
        payload = [{'id': item_id, 'item': 1}]
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

    def test_categories_delete_cascade(self):
        cat_path = '/api/v1/categories'
        item_path = '/api/v1/items'
        headers = {'x-opp-phrase': "123"}

        # Request getall categories, expect empty list initially
        response = self.client.get(cat_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add two categories
        data = {'payload': '["cat1", "cat2"]'}
        response = self.client.put(cat_path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify new categories
        response = self.client.get(cat_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 2)
        c1, c2 = data['categories']

        # Add four items (two per category)
        items = [{'item': "i1", 'category_id': c1['id']},
                 {'item': "i2", 'category_id': c1['id']},
                 {'item': "i3", 'category_id': c2['id']},
                 {'item': "i4", 'category_id': c2['id']}]
        data = {'payload': json.dumps(items)}
        response = self.client.put(item_path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify new items
        response = self.client.get(item_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 4)

        i1, i2, i3, i4 = data['items']

        self.assertEqual(i1['item'], "i1")
        self.assertEqual(i1['category'], c1['category'])
        self.assertEqual(i1['category_id'], c1['id'])

        self.assertEqual(i2['item'], "i2")
        self.assertEqual(i2['category'], c1['category'])
        self.assertEqual(i2['category_id'], c1['id'])

        self.assertEqual(i3['item'], "i3")
        self.assertEqual(i3['category'], c2['category'])
        self.assertEqual(i3['category_id'], c2['id'])

        self.assertEqual(i4['item'], "i4")
        self.assertEqual(i4['category'], c2['category'])
        self.assertEqual(i4['category_id'], c2['id'])

        # Delete category 1 with cascade
        payload = {'cascade': True, 'ids': [c1['id']]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(cat_path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify updated category list (expect 1)
        response = self.client.get(cat_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['id'], c2['id'])

        # Verify updated items list (expect 2)
        response = self.client.get(item_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 2)
        i3, i4 = data['items']
        self.assertEqual(i3['item'], "i3")
        self.assertEqual(i3['category'], c2['category'])
        self.assertEqual(i3['category_id'], c2['id'])
        self.assertEqual(i4['item'], "i4")
        self.assertEqual(i4['category'], c2['category'])
        self.assertEqual(i4['category_id'], c2['id'])

        # Delete category 2 without cascade
        payload = {'cascade': False, 'ids': [c2['id']]}
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(cat_path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify empty category list
        response = self.client.get(cat_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 0)

        # Verify updated items list (expect 2 with no categories)
        response = self.client.get(item_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 2)
        i3, i4 = data['items']
        self.assertEqual(i3['item'], "i3")
        self.assertEqual(i3['category'], None)
        self.assertEqual(i3['category_id'], None)
        self.assertEqual(i4['item'], "i4")
        self.assertEqual(i4['category'], None)
        self.assertEqual(i4['category_id'], None)

        # Delete remaining two items to clean up
        data = {'payload': json.dumps([i3['id'], i4['id']])}
        response = self.client.delete(item_path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        response = self.client.get(item_path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 0)
