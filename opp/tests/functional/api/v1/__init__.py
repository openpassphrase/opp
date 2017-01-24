import json
import os
import tempfile
import unittest

from opp.api import v1 as api
from opp.common import utils


class BackendApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test directory, config file and database
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        with open(cls.conf_filepath, 'wb') as conf_file:
            conf_file.write("sql_connect: 'sqlite:///%s'" % cls.db_filepath)
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

        # Global headers variable
        cls.hdrs = None

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

    def _get(self, path, code=200):
        resp = self.client.get(path, headers=self.hdrs)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data)

    def _put(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.put(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data)

    def _post(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.post(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data)

    def _delete(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.delete(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data)
