import os
import tempfile
import unittest

from opp.common import utils


class TestDbManager(unittest.TestCase):

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
        utils.execute("opp-db --config_file %s add-user -u u -p p"
                      % self.conf_filepath)
        self._assert_user_exists('u')
        utils.execute("opp-db --config_file %s del-user -u u -p p"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')

    def test_add_duplicate_user(self):
        utils.execute("opp-db --config_file %s add-user -u u -p p"
                      % self.conf_filepath)
        try:
            utils.execute("opp-db --config_file %s add-user -u u -p p"
                          % self.conf_filepath)
            self.assertFail("Expected user already exists message!")
        except Exception as e:
            self.assertIn("Error: user already exists!", str(e))

        # Cleanup
        utils.execute("opp-db --config_file %s del-user -u u -p p"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')

    def test_del_missing_user(self):
        try:
            utils.execute("opp-db --config_file %s del-user -u u -p p"
                          % self.conf_filepath)
            self.assertFail("Expected user does not exist message!")
        except Exception as e:
            self.assertIn("Error: user does not exist!", str(e))

    def test_del_user_incorrect_password(self):
        utils.execute("opp-db --config_file %s add-user -u u -p p"
                      % self.conf_filepath)
        try:
            utils.execute("opp-db --config_file %s del-user -u u -p x"
                          % self.conf_filepath)
            self.assertFail("Expected incorrect password message!")
        except Exception as e:
            self.assertIn("Error: incorrect password!", str(e))

        # Cleanup
        utils.execute("opp-db --config_file %s del-user -u u -p p"
                      % self.conf_filepath)
        self._assert_user_does_not_exist('u')
