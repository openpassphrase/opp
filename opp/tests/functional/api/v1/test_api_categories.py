import json
import os
import tempfile
import unittest

from opp.api import v1 as api
from opp.common import utils


class TestBackendApiCategories(unittest.TestCase):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    @classmethod
    def setUpClass(cls):
        # Create test directory, config file and database
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        cls.connection = ("sql_connect: 'sqlite:///%s'" % cls.db_filepath)
        with open(cls.conf_filepath, 'wb') as conf_file:
            conf_file.write(cls.connection)
            conf_file.flush()
        os.environ['OPP_TOP_CONFIG'] = cls.conf_filepath
        utils.execute("opp-db --config_file %s init" % cls.conf_filepath)

        # Create a test client and propgate exceptions to it
        cls.client = api.app.test_client()
        cls.client.testing = True

        # Create a user, authenticate and store JWT
        headers = {"Content-Type": "application/json"}
        data = json.dumps({'username': "u", 'password': "p"})
        cls.client.put("/users", headers=headers, data=data)
        response = cls.client.post("/login", headers=headers, data=data)
        data = json.loads(response.data)
        cls.jwt = data['access_token']

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

    def test_disallowed_methods_categories(self):
        rpat = self.client.patch('/api/v1/categories')
        self.assertEqual(rpat.status_code, 405)

    def test_categories_crud(self):
        path = '/api/v1/categories'
        hdrs = {'x-opp-phrase': "123",
                'x-opp-jwt': self.jwt,
                'Content-Type': "application/json"}

        # Request getall categories, expect empty list initially
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add 3 categories, check for successful response
        data = {'payload': ["cat1", "cat2", "cat3"]}
        response = self.client.put(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 categories
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
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
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Check all 3 categories
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 3)
        cat1, cat2, cat3 = data['categories']
        self.assertEqual(cat1['name'], "new_cat1")
        self.assertEqual(cat2['name'], "cat2")
        self.assertEqual(cat3['name'], "new_cat3")

        # Delete categories 1 & 3
        payload = {'cascade': False, 'ids': [cat1['id'], cat3['id']]}
        data = {'payload': payload}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Get all categories, only 1 sould remain
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], "cat2")

        # Clean up by deleting category 2
        payload = {'cascade': False, 'ids': [cat2['id']]}
        data = {'payload': payload}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

    def test_categories_error_conditions(self):
        path = '/api/v1/categories'
        hdrs = {'x-opp-phrase': "123",
                'x-opp-jwt': self.jwt,
                'Content-Type': "application/json"}

        # Try to PUT with empty category list
        data = {'payload': ["cat1", ""]}
        response = self.client.put(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category name in list!")

        # Try to PUT with invalid category name in list (int instead of string)
        data = {'payload': ["cat1", 2]}
        response = self.client.put(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category name in list!")

        # Add a category
        data = {'payload': ["cat4"]}
        response = self.client.put(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Retrieve all categories, expect only the one that was just added
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['name'], "cat4")
        cat_id = data['categories'][0]['id']

        # Try to POST with missing category id
        data = {'payload': [{'noid': cat_id}]}
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id in list!")

        # Try to POST with empty category id
        data = {'payload': [{'id': ""}]}
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id in list!")

        # Try to POST with missing category name
        data = {'payload': [{'id': cat_id, 'nocategory': "new_cat4"}]}
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category name in list!")

        # Try to POST with empty category name
        data = {'payload': [{'id': cat_id, 'name': ""}]}
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category name in list!")

        # Try to POST with invalid category name in list
        data = {'payload': [{'id': cat_id, 'name': 1}]}
        response = self.client.post(path, headers=hdrs, data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category name in list!")

        # Try to delete with invalid payload (list form)
        data = {'payload': [1, 2, 3]}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'],
                         "Payload should not be in list form!")

        # Try to delete with missing cascade value
        data = {'payload': {'notcascade': False, 'ids': [2]}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing cascade value!")

        # Try to delete with invalid cascade value (string instead of boolean)
        data = {'payload': {'cascade': "False", 'ids': [2]}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid cascade value!")

        # Try to delete with missing category id list
        data = {'payload': {'cascade': False, 'notids': [2]}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing category id list!")

        # Try to delete with empty category id list
        data = {'payload': {'cascade': False, 'ids': []}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty category id list!")

        # Try to delete with invalid category id list
        data = {'payload': {'cascade': False, 'ids': "1"}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid category id list!")

        # Clean up by deleting the category
        data = {'payload': {'cascade': False, 'ids': [cat_id]}}
        response = self.client.delete(path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Request getall categories, expect empty list
        response = self.client.get(path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

    def test_categories_delete_cascade(self):
        cat_path = '/api/v1/categories'
        item_path = '/api/v1/items'
        hdrs = {'x-opp-phrase': "123",
                'x-opp-jwt': self.jwt,
                'Content-Type': "application/json"}

        # Request getall categories, expect empty list initially
        response = self.client.get(cat_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add two categories
        data = {'payload': ["cat1", "cat2"]}
        response = self.client.put(cat_path, headers=hdrs,
                                   data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify new categories
        response = self.client.get(cat_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 2)
        c1, c2 = data['categories']

        # Add four items (two per category)
        items = [{'name': "i1", 'category_id': c1['id']},
                 {'name': "i2", 'category_id': c1['id']},
                 {'name': "i3", 'category_id': c2['id']},
                 {'name': "i4", 'category_id': c2['id']}]
        data = {'payload': items}
        response = self.client.put(item_path, headers=hdrs,
                                   data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify new items
        response = self.client.get(item_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
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
        response = self.client.delete(cat_path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify updated category list (expect 1)
        response = self.client.get(cat_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 1)
        self.assertEqual(data['categories'][0]['id'], c2['id'])

        # Verify updated items list (expect 2)
        response = self.client.get(item_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
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
        response = self.client.delete(cat_path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Verify empty category list
        response = self.client.get(cat_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 0)

        # Verify updated items list (expect 2 with no categories)
        response = self.client.get(item_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 2)
        i3, i4 = data['items']
        self.assertEqual(i3['name'], "i3")
        self.assertEqual(i3['category']['id'], None)
        self.assertEqual(i4['name'], "i4")
        self.assertEqual(i4['category']['id'], None)

        # Delete remaining two items to clean up
        data = {'payload': [i3['id'], i4['id']]}
        response = self.client.delete(item_path, headers=hdrs,
                                      data=json.dumps(data))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        response = self.client.get(item_path, headers=hdrs)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['items']), 0)
