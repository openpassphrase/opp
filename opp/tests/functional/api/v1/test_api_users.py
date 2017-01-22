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
        data = {'username': "user", 'current_password': "pass",
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

        # Try to create user with missing username
        data = {'nousername': "user", 'password': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to create user with empty username
        data = {'username': "", 'password': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to create user with missing password
        data = {'username': "user", 'nopassword': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing password!")

        # Try to create user with empty password
        data = {'username': "user", 'password': ""}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty password!")

        # Try to add the same user twice
        data = {'username': "user", 'password': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")

        data = {'username': "user", 'password': "pass"}
        response = self.client.put(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User already exists!")

        # Try to update user with missing username
        data = {'nousername': "user", 'password': "pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to update user with empty username
        data = {'username': "", 'password': "pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to update user with missing current password
        data = {'username': "user", 'password': "pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing current password!")

        # Try to update user with empty current password
        data = {'username': "user", 'current_password': ""}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty current password!")

        # Try to update user with missing new password
        data = {'username': "user", 'current_password': "pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing new password!")

        # Try to update user with empty new password
        data = {'username': "user", 'current_password': "pass",
                'new_password': ""}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty new password!")

        # Try to update non-existing user
        data = {'username': "nouser", 'current_password': "pass",
                'new_password': "new_pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User doesn't exist!")

        # Try to update user with invalid current password
        data = {'username': "user", 'current_password': "invalid",
                'new_password': "new_pass"}
        response = self.client.post(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid password!")

        # Try to delete user with missing username
        data = {'nousername': "user", 'password': "pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to delete user with empty username
        data = {'username': "", 'password': "pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to delete user with missing password
        data = {'username': "user", 'nopassword': "pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing password!")

        # Try to delete user with empty password
        data = {'username': "user", 'password': ""}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty password!")

        # Try to delete non-existing user
        data = {'username': "nouser", 'password': "pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User doesn't exist!")

        # Delete the user to clean up
        data = {'username': "user", 'password': "pass"}
        response = self.client.delete(path, data=data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['result'], "success")
