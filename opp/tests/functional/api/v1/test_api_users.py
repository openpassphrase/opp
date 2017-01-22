import json
import os
import tempfile
import unittest

from opp.api import v1 as api
from opp.common import utils


class TestBackendApiUsers(unittest.TestCase):

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

    def test_disallowed_methods_users(self):
        rget = self.client.patch('/users')
        rpat = self.client.patch('/users')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_users_cud(self):
        path = '/users'

        # Add a user, check for successful response
        data = {'username': "user", 'password': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Update the user
        data = {'username': "user", 'old_password': "pass",
                'new_password': "new_pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        # Delete the user
        data = {'username': "user", 'password': "new_pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

    def test_users_error_conditions(self):
        path = '/users'
