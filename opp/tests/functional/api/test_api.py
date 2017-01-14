import json
import os
import tempfile
import unittest

from opp import api
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
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         '{"status": "OpenPassPhrase service is running"}')

    def test_disallowed_methods_categories(self):
        rget = self.client.get('/categories')
        rput = self.client.put('/categories')
        rdel = self.client.delete('/categories')
        rpat = self.client.patch('/categories')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rput.status_code, 405)
        self.assertEqual(rdel.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_disallowed_methods_entries(self):
        rget = self.client.get('/entries')
        rput = self.client.put('/entries')
        rdel = self.client.delete('/entries')
        rpat = self.client.patch('/entries')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rput.status_code, 405)
        self.assertEqual(rdel.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_categories_basic(self):
        # Request getall categories
        data = {'phrase': '123', 'action': 'getall'}
        response = self.client.post('/categories', data=data)

        # Expect empty list initially
        self.assertEqual(response.status_code, 200)
        data = '{"result": "success", "categories": []}'
        self.assertEqual(response.data, data)

        # Add 3 categories, check for successful response
        data = {'phrase': '123', 'action': 'create',
                'payload': '["cat1", "cat2", "cat3"]'}
        response = self.client.post('/categories', data=data)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['payload']), 3)
        cat1, cat2, cat3 = data['payload']
        self.assertEqual(cat1['category'], "cat1")
        self.assertEqual(cat2['category'], "cat2")
        self.assertEqual(cat3['category'], "cat3")
        self.assertEqual(cat1['status'], "success: created")
        self.assertEqual(cat2['status'], "success: created")
        self.assertEqual(cat3['status'], "success: created")
