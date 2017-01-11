import os
import tempfile
import testtools

from opp.db import api, models
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

    def test_categories_basic(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Expect empty category list initially
        categories = api.category_getall(session=session)
        self.assertEqual(categories, [])

        # Insert and retrieve a category
        category = models.Category(blob='blob')
        api.category_create_update([category], session=session)
        categories = api.category_getall(session=session)
        self.assertEqual(len(categories), 1)

        # Update and check the category
        category.blob = 'new blob'
        api.category_create_update([category], session=session)
        categories = api.category_getall(session=session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].blob, 'new blob')

        # Delete the category
        api.category_delete(categories, session=session)
        categories = api.category_getall(session=session)
        self.assertEqual(len(categories), 0)

        session.close()

    def test_categories_get_filter(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Insert several categories
        categories = [models.Category(blob='blob0'),
                      models.Category(blob='blob1'),
                      models.Category(blob='blob2')]
        api.category_create_update(categories, session=session)

        # Retrieve first and last categories only
        ids = [1, 3]
        categories = api.category_getall(filter_ids=ids, session=session)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].blob, 'blob0')
        self.assertEqual(categories[1].blob, 'blob2')

        session.close()

    def test_categories_delete_by_id(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Insert several categories
        categories = [models.Category(blob='blob3'),
                      models.Category(blob='blob4'),
                      models.Category(blob='blob5')]
        api.category_create_update(categories, session=session)

        # Delete first and last categories only
        ids = [1, 3]
        api.category_delete_by_id(filter_ids=ids, session=session)

        categories = api.category_getall(session=session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].blob, 'blob4')

        session.close()

    def test_entries_basic(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Expect empty entry list initially
        entries = api.entry_getall(session=session)
        self.assertEqual(entries, [])

        # Insert and retrieve an entry
        entry = models.Entry(blob='blob', category_id=None)
        api.entry_create_update([entry], session=session)
        entries = api.entry_getall(session=session)
        self.assertEqual(len(entries), 1)

        # Update and check the entry
        entry.blob = 'new blob'
        entry.category_id = 999
        api.entry_create_update([entry], session=session)
        entries = api.entry_getall(session=session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, 'new blob')
        self.assertEqual(entries[0].category_id, 999)

        # Update entry with valid category
        category = models.Category(blob='blah')
        api.category_create_update([category], session=session)
        entry.category_id = 1
        api.entry_create_update([entry], session=session)
        entries = api.entry_getall(session=session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, 'new blob')
        self.assertEqual(entries[0].category_id, 1)
        self.assertIsNotNone(entries[0].category)

        # Delete the entry
        api.entry_delete(entries, session=session)
        entries = api.entry_getall(session=session)
        self.assertEqual(len(entries), 0)

        session.close()

    def test_entries_get_filter(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Insert several entries
        entries = [models.Entry(blob='blob0'),
                   models.Entry(blob='blob1'),
                   models.Entry(blob='blob2')]
        api.entry_create_update(entries, session=session)

        # Retrieve first and last entries only
        ids = [1, 3]
        entries = api.entry_getall(filter_ids=ids, session=session)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].blob, 'blob0')
        self.assertEqual(entries[1].blob, 'blob2')

        session.close()

    def test_entries_delete_by_id(self):
        conf = opp_config.OppConfig(self.conf_filepath)
        session = api.get_session(conf)

        # Insert several entries
        entries = [models.Entry(blob='blob3'),
                   models.Entry(blob='blob4'),
                   models.Entry(blob='blob5')]
        api.entry_create_update(entries, session=session)

        # Delete first and last entries only
        ids = [1, 3]
        api.entry_delete_by_id(filter_ids=ids, session=session)

        entries = api.entry_getall(session=session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, 'blob4')

        session.close()
