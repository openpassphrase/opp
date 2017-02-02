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

import os
import tempfile
import unittest

from opp.db import api, models
from opp.common import opp_config, utils


def with_session(function):
    def wrapper(self):
        with self.s.begin():
            function(self)
    return wrapper


class TestCase(unittest.TestCase):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        cls.connection = ("[DEFAULT]\ndb_connect = sqlite:///%s" %
                          cls.db_filepath)
        with open(cls.conf_filepath, 'w') as conf_file:
            conf_file.write(cls.connection)
            conf_file.flush()
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
        conf = opp_config.OppConfig(self.conf_filepath)
        self.s = api.get_scoped_session(conf)

    def tearDown(self):
        pass

    @with_session
    def test_users_basic(self):
        # Insert and retrieve an user
        user = models.User(username="user", password="pass")
        api.user_create(self.s, user)
        user = api.user_get_by_username(self.s, user.username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "user")
        self.assertEqual(user.password, "pass")

        # Update and check the user
        user.username = "new user"
        user.password = "new_pass"
        api.user_update(self.s, user)
        new_user = api.user_get_by_id(self.s, user.id)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, user.username)
        self.assertEqual(new_user.password, user.password)
        self.assertEqual(new_user.id, user.id)

        # Clean up and verify
        api.user_delete_by_username(self.s, user.username)
        user = api.user_get_by_id(self.s, user.id)
        self.assertIsNone(user)
