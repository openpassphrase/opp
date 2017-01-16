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

    def test_disallowed_methods_entries(self):
        rpat = self.client.patch('/api/v1/entries')
        self.assertEqual(rpat.status_code, 405)

    def test_categories_basic(self):
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

    def test_categories_error(self):
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

    def test_entries_basic(self):
        path = '/api/v1/entries'
        headers = {'x-opp-phrase': "123"}

        # Request getall entries, expect empty list initially
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['entries'], [])

        # Add 3 entries, check for successful response
        data = {'payload':
                '[{"entry": "e1"}, {"entry": "e2"}, {"entry": "e3"}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Update entries 1 & 3
        payload = [{'id': 1, 'entry': "new_e1"},
                   {'id': 3, 'entry': "new_e3"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 entries
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['entries']), 3)
        ent1, ent2, ent3 = data['entries']
        self.assertEqual(ent1['entry'], "new_e1")
        self.assertEqual(ent2['entry'], "e2")
        self.assertEqual(ent3['entry'], "new_e3")

        # Delete entries 1 & 3
        payload = [ent1['id'], ent3['id']]
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Get all entries, only 1 sould remain
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(data['entries'][0]['entry'], "e2")

        # Clean up by deleting entry 2
        payload = [ent2['id']]
        data = {'payload': json.dumps(payload)}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall entries, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['entries'], [])

    def test_entries_error(self):
        path = '/api/v1/entries'
        headers = {'x-opp-phrase': "123"}

        # Try to PUT with missing entry in list
        data = {'payload': '[{}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing entry data in list!")

        # Try to PUT with empty entry in list
        data = {'payload': '[{"entry": ""}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty entry data in list!")

        # Try to PUT with invalid entry in list (int instead of string)
        data = {'payload': '[{"entry": 2}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid entry data in list!")

        # Add an entry
        data = {'payload': '[{"entry": "e4"}]'}
        response = self.client.put(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Retrieve all entries, expect only the one that was just added
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(data['entries'][0]['entry'], "e4")
        ent_id = data['entries'][0]['id']

        # Try to POST with missing entry id
        payload = [{'noid': ent_id}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing entry id in list!")

        # Try to POST with empty entry id
        payload = [{'id': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty entry id in list!")

        # Try to POST with missing entry
        payload = [{'id': ent_id, 'noentry': "new_e4"}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing entry in list!")

        # Try to POST with empty entry
        payload = [{'id': ent_id, 'entry': ""}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty entry in list!")

        # Try to POST with invalid entry in list
        payload = [{'id': ent_id, 'entry': 1}]
        data = {'payload': json.dumps(payload)}
        response = self.client.post(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid entry data in list!")

        # Clean up by deleting the entry
        data = {'payload': json.dumps([ent_id])}
        response = self.client.delete(path, headers=headers, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall entries, expect empty list
        response = self.client.get(path, headers=headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['entries'], [])
