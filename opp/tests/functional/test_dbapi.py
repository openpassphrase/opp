import os
import tempfile
import testtools

from opp.db import api
from opp.common import opp_config, utils


class TestDbApi(testtools.TestCase):

    def setUp(self):
        super(TestDbApi, self).setUp()
        self.test_dir = tempfile.mkdtemp(prefix='opp_')
        self.conf_filepath = os.path.join(self.test_dir, 'opp.cfg')
        self.db_filepath = os.path.join(self.test_dir, 'test.sqlite')
        self.connection = ("sql_connect: 'sqlite:///%s'" % self.db_filepath)
        with open(self.conf_filepath, 'wb') as conf_file:
            conf_file.write(self.connection)
            conf_file.flush()
        utils.execute("opp-db --config_file %s init" % self.conf_filepath)

    def tearDown(self):
        os.remove(self.conf_filepath)
        os.remove(self.db_filepath)
        os.rmdir(self.test_dir)
        super(TestDbApi, self).tearDown()
        pass

    def test_category_getall(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        api.category_getall(conf=conf)
