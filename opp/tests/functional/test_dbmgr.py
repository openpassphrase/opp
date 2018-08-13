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

from opp.common import aescipher, opp_config, utils
from opp.db import api, models


class TestCase(unittest.TestCase):

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
        os.remove(cls.conf_filepath)
        os.remove(cls.db_filepath)
        os.rmdir(cls.test_dir)

    def _assert_table_exists(self, db_table):
        cmd = ("sqlite3 {0} \"SELECT name FROM sqlite_master WHERE "
               "type='table' AND name='{1}'\"").format(self.db_filepath,
                                                       db_table)
        code, out, err = utils.execute(cmd)
        msg = "Expected table {0} was not found in the schema".format(db_table)
        self.assertEqual(out.rstrip().decode(), db_table, msg)

    def _assert_user_exists(self, name):
        cmd = ("sqlite3 {0} \"SELECT username FROM users WHERE "
               "username='{1}'\"").format(self.db_filepath, name)
        code, out, err = utils.execute(cmd)
        msg = "Expected user was not found in the users table"
        self.assertEqual(out.rstrip().decode(), name, msg)

    def _assert_user_does_not_exist(self, name):
        cmd = ("sqlite3 {0} \"SELECT username FROM users WHERE "
               "username='{1}'\"").format(self.db_filepath, name)
        code, out, err = utils.execute(cmd)
        msg = "Unxpected user found in the users table"
        self.assertNotEqual(out.rstrip().decode(), name, msg)

    def test_schema_creation(self):
        for table in ['categories', 'items']:
            self._assert_table_exists(table)

    def test_add_del_user(self):
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % self.conf_filepath)
        self._assert_user_exists('u')

        utils.execute("opp-db --config_file %s del-user -uu -pp"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')

    def test_add_duplicate_user(self):
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % self.conf_filepath)
        try:
            utils.execute("opp-db --config_file %s add-user -uu -pp "
                          "--phrase=123456" % self.conf_filepath)
            self.assertFail("Expected user already exists message!")
        except Exception as e:
            self.assertIn("Error: user already exists!", str(e))

        # Cleanup
        utils.execute("opp-db --config_file %s del-user -uu -pp"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')

    def test_add_user_passphrase_too_short(self):
        try:
            utils.execute("opp-db --config_file %s add-user -uu -pp "
                          "--phrase=12345" % self.conf_filepath)
            self.assertFail("Expected passphrase too short message!")
        except Exception as e:
            self.assertIn("Error: passphrase must be at least 6"
                          " characters long!", str(e))

    def test_del_missing_user(self):
        try:
            utils.execute("opp-db --config_file %s del-user -uu -pp"
                          % self.conf_filepath)
            self.assertFail("Expected user does not exist message!")
        except Exception as e:
            self.assertIn("Error: user does not exist!", str(e))

    def test_del_user_incorrect_password(self):
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % self.conf_filepath)
        try:
            utils.execute("opp-db --config_file %s del-user -uu -px"
                          % self.conf_filepath)
            self.assertFail("Expected incorrect password message!")
        except Exception as e:
            self.assertIn("Error: incorrect password!", str(e))

        # Cleanup
        utils.execute("opp-db --config_file %s del-user -uu -pp"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')

    def test_update_user(self):
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % self.conf_filepath)

        # Try to update with no "new" parameters supplied
        try:
            utils.execute("opp-db --config_file %s update-user -uu -pp "
                          % self.conf_filepath)
            self.assertFail("Expected 'at least one of...' error message!")
        except Exception as e:
            msg = ("Error: at least one of: [--new_username, "
                   "--new_password] options must be specified!")
            self.assertIn(msg, str(e))

        # Try to update with incorrect password
        try:
            utils.execute("opp-db --config_file %s update-user -uu -pp1 "
                          "--new_password blah" % self.conf_filepath)
            self.assertFail("Expected 'incorrect password' errro message!")
        except Exception as e:
            self.assertIn("Error: incorrect password!", str(e))

        # Update username and password
        self._assert_user_does_not_exist('u1')
        utils.execute("opp-db --config_file %s update-user -uu -pp "
                      "--new_username u1 --new_password p1"
                      % self.conf_filepath)
        self._assert_user_exists('u1')
        self._assert_user_does_not_exist('u')

        # Cleanup, this should not raise if above password update succeeded
        utils.execute("opp-db --config_file %s del-user -uu1 -pp1"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u1')

    def test_update_phrase(self):
        config = opp_config.OppConfig(self.conf_filepath)

        # Add user
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % self.conf_filepath)

        old = aescipher.AESCipher("123456")
        new = aescipher.AESCipher("654321")

        # Add category and item using old passphrase
        session = api.get_scoped_session(config)
        category = models.Category(name=old.encrypt("cat1"))
        item = models.Item(
            name=old.encrypt("item1"),
            url=old.encrypt("url1"),
            account=old.encrypt("account1"),
            username=old.encrypt("username1"),
            password=old.encrypt("password1"),
            blob=old.encrypt("blob1"))
        with session.begin():
            user = api.user_get_by_username(session, 'u')
            category.user = user
            item.user = user
            api.category_create(session, [category])
            api.item_create(session, [item])

        # Update passphrase
        utils.execute("opp-db --config_file %s update-phrase -uu -pp "
                      "--old_phrase=123456 --new_phrase=654321" %
                      self.conf_filepath)

        # Check data using new passphrase
        session = api.get_scoped_session(config)
        with session.begin():
            user = api.user_get_by_username(session, 'u')
            category = api.category_getall(session, user)[0]
            self.assertEqual(new.decrypt(category.name), "cat1")
            item = api.item_getall(session, user)[0]
            self.assertEqual(new.decrypt(item.name), "item1")
            self.assertEqual(new.decrypt(item.url), "url1")
            self.assertEqual(new.decrypt(item.account), "account1")
            self.assertEqual(new.decrypt(item.username), "username1")
            self.assertEqual(new.decrypt(item.password), "password1")
            self.assertEqual(new.decrypt(item.blob), "blob1")

        # Cleanup
        utils.execute("opp-db --config_file %s del-user -uu -pp"
                      " --remove_data" % self.conf_filepath)
        self._assert_user_does_not_exist('u')
