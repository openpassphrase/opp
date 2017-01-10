import os
import tempfile
import testtools

from opp.common import utils


class TestDbManager(testtools.TestCase):

    def setUp(self):
        super(TestDbManager, self).setUp()
        self.test_dir = tempfile.mkdtemp(prefix='opp_')
        self.conf_filepath = os.path.join(self.test_dir, 'opp.cfg')
        self.db_filepath = os.path.join(self.test_dir, 'test.sqlite')
        self.connection = ("sql_connect: 'sqlite:///%s'" % self.db_filepath)

    def tearDown(self):
        os.remove(self.conf_filepath)
        os.remove(self.db_filepath)
        os.rmdir(self.test_dir)
        super(TestDbManager, self).tearDown()
        pass

    def _init_db(self):
        with open(self.conf_filepath, 'wb') as conf_file:
            conf_file.write(self.connection)
            conf_file.flush()

        utils.execute("opp-db --config_file %s init" % self.conf_filepath)

    def _assert_table_exists(self, db_table):
        cmd = ("sqlite3 {0} \"SELECT name FROM sqlite_master WHERE "
               "type='table' AND name='{1}'\"").format(self.db_filepath,
                                                       db_table)
        code, out, err = utils.execute(cmd)
        msg = "Expected table {0} was not found in the schema".format(db_table)
        self.assertEqual(out.rstrip(), db_table, msg)

    def test_schema_creation(self):
        self._init_db()

        for table in ['categories', 'entries']:
            self._assert_table_exists(table)
