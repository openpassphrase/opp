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

import json
import os
import tempfile
import unittest

from opp.flask.json_server import app
from opp.common import utils


class BackendApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create test directory, config file and database
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        with open(cls.conf_filepath, 'w') as conf_file:
            conf_file.write("[DEFAULT]\ndb_connect = sqlite:///%s" %
                            cls.db_filepath)
            conf_file.flush()
        os.environ['OPP_TOP_CONFIG'] = cls.conf_filepath
        # Create database and a user
        utils.execute("opp-db --config_file %s init" % cls.conf_filepath)
        utils.execute("opp-db --config_file %s add-user -u u -p p"
                      % cls.conf_filepath)

        # Create a test client and propgate exceptions to it
        cls.client = app.test_client()
        cls.client.testing = True

        # Authenticate the user and store JWT
        headers = {"Content-Type": "application/json"}
        data = json.dumps({'username': "u", 'password': "p"})
        response = cls.client.post("/v1/auth", headers=headers, data=data)
        data = json.loads(response.data.decode())
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
        return json.loads(resp.data.decode())

    def _put(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.put(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data.decode())

    def _post(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.post(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data.decode())

    def _delete(self, path, data=None, code=200):
        if data:
            data = json.dumps(data)
        resp = self.client.delete(path, headers=self.hdrs, data=data)
        self.assertEqual(resp.status_code, code)
        return json.loads(resp.data.decode())
