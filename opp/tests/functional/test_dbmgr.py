import os
import tempfile
import unittest

from opp.common import utils


class TestDbManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix='opp_')
        self.conf_filepath = os.path.join(self.test_dir, 'opp.cfg')
        self.db_filepath = os.path.join(self.test_dir, 'test.sqlite')
        self.connection = ("[DEFAULT]\nsql_connect = sqlite:///%s" %
                           self.db_filepath)

    def tearDown(self):
        os.remove(self.conf_filepath)
        os.remove(self.db_filepath)
        os.rmdir(self.test_dir)

    def _init_db(self):
        with open(self.conf_filepath, 'w') as conf_file:
            conf_file.write(self.connection)
            conf_file.flush()

        utils.execute("opp-db --config_file %s init" % self.conf_filepath)

    def _assert_table_exists(self, db_table):
        cmd = ("sqlite3 {0} \"SELECT name FROM sqlite_master WHERE "
               "type='table' AND name='{1}'\"").format(self.db_filepath,
                                                       db_table)
        code, out, err = utils.execute(cmd)
        msg = "Expected table {0} was not found in the schema".format(db_table)
        self.assertEqual(out.rstrip().decode(), db_table, msg)

    def test_schema_creation(self):
        self._init_db()

        for table in ['categories', 'items']:
            self._assert_table_exists(table)
