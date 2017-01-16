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
        connection = ("sql_connect: 'sqlite:///%s'" % self.db_filepath)
        with open(self.conf_filepath, 'wb') as conf_file:
            conf_file.write(connection)
            conf_file.flush()
        utils.execute("opp-db --config_file %s init" % self.conf_filepath)
        conf = opp_config.OppConfig(self.conf_filepath)
        self.session = api.get_session(conf)

    def tearDown(self):
        self.session.close()
        os.remove(self.conf_filepath)
        os.remove(self.db_filepath)
        os.rmdir(self.test_dir)
        super(TestDbApi, self).tearDown()

    def test_categories_basic(self):
        # Expect empty category list initially
        categories = api.category_getall(session=self.session)
        self.assertEqual(categories, [])

        # Insert and retrieve a category
        category = models.Category(blob="blob")
        api.category_create([category], session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)

        # Update and check the category
        category.blob = 'new blob'
        api.category_update([category], session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].blob, "new blob")

        # Delete the category
        api.category_delete(categories, cascade=False, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

    def test_categories_get_filter(self):
        # Insert several categories
        categories = [models.Category(blob="blob0"),
                      models.Category(blob="blob1"),
                      models.Category(blob="blob2")]
        api.category_create(categories, session=self.session)

        # Retrieve first and last categories only
        ids = [1, 3]
        categories = api.category_getall(filter_ids=ids, session=self.session)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].blob, "blob0")
        self.assertEqual(categories[1].blob, "blob2")

    def test_categories_delete_by_id(self):
        # Insert several categories
        categories = [models.Category(blob="blob3"),
                      models.Category(blob="blob4"),
                      models.Category(blob="blob5")]
        api.category_create(categories, session=self.session)

        # Delete first and last categories only
        ids = [1, 3]
        api.category_delete_by_id(ids, cascade=False, session=self.session)

        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].blob, "blob4")

    def test_entries_basic(self):
        # Expect empty entry list initially
        entries = api.entry_getall(session=self.session)
        self.assertEqual(entries, [])

        # Insert and retrieve an entry
        entry = models.Entry(blob="blob", category_id=None)
        api.entry_create([entry], session=self.session)
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 1)

        # Update and check the entry
        entry.blob = "new blob"
        entry.category_id = 999
        api.entry_update([entry], session=self.session)
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, "new blob")
        self.assertEqual(entries[0].category_id, 999)

        # Update entry with valid category
        category = models.Category(blob="blah")
        api.category_create([category], session=self.session)
        entry.category_id = 1
        api.entry_update([entry], session=self.session)
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, "new blob")
        self.assertEqual(entries[0].category_id, 1)
        self.assertIsNotNone(entries[0].category)

        # Delete the entry
        api.entry_delete(entries, session=self.session)
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 0)

    def test_entries_get_filter(self):
        # Insert several entries
        entries = [models.Entry(blob="blob0"),
                   models.Entry(blob="blob1"),
                   models.Entry(blob="blob2")]
        api.entry_create(entries, session=self.session)

        # Retrieve first and last entries only
        ids = [1, 3]
        entries = api.entry_getall(filter_ids=ids, session=self.session)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].blob, "blob0")
        self.assertEqual(entries[1].blob, "blob2")

    def test_entries_delete_by_id(self):
        # Insert several entries
        entries = [models.Entry(blob="blob3"),
                   models.Entry(blob="blob4"),
                   models.Entry(blob="blob5")]
        api.entry_create(entries, session=self.session)

        # Delete first and last entries only
        ids = [1, 3]
        api.entry_delete_by_id(filter_ids=ids, session=self.session)

        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].blob, "blob4")

    def test_categories_delete_cascade(self):
        # Insert categories
        categories = [models.Category(blob="cat1"),
                      models.Category(blob="cat2")]
        api.category_create(categories, session=self.session)

        # Verify categories
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].blob, "cat1")
        self.assertEqual(categories[1].blob, "cat2")

        # Insert entries
        entries = [models.Entry(blob="ent1", category_id=1),
                   models.Entry(blob="ent2", category_id=1),
                   models.Entry(blob="ent3", category_id=2),
                   models.Entry(blob="ent4", category_id=2)]
        api.entry_create(entries, session=self.session)

        # Verify entries
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 4)

        e1, e2, e3, e4 = entries

        self.assertEqual(e1.blob, "ent1")
        self.assertEqual(e1.category_id, 1)
        self.assertIsNotNone(e1.category)
        self.assertEqual(e1.category.id, 1)

        self.assertEqual(e2.blob, "ent2")
        self.assertEqual(e2.category_id, 1)
        self.assertIsNotNone(e2.category)
        self.assertEqual(e1.category.id, 1)

        self.assertEqual(e3.blob, "ent3")
        self.assertEqual(e3.category_id, 2)
        self.assertIsNotNone(e3.category)
        self.assertEqual(e3.category.id, 2)

        self.assertEqual(e4.blob, "ent4")
        self.assertEqual(e4.category_id, 2)
        self.assertIsNotNone(e4.category)
        self.assertEqual(e4.category.id, 2)

        # Delete category 1 with cascade
        api.category_delete(categories[:1], cascade=True,
                            session=self.session)

        # Verify only 1 category remains
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].blob, "cat2")

        # Verify entries 1 & 2 were deleted through cascade action
        # and that entries 3 & 4 remain unchanged
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 2)
        e3, e4 = entries
        self.assertEqual(e3.blob, "ent3")
        self.assertEqual(e3.category_id, 2)
        self.assertIsNotNone(e3.category)
        self.assertEqual(e3.category.id, 2)
        self.assertEqual(e4.blob, "ent4")
        self.assertEqual(e4.category_id, 2)
        self.assertIsNotNone(e4.category)
        self.assertEqual(e4.category.id, 2)

        # Delete category 2 without cascade
        api.category_delete(categories, cascade=False,
                            session=self.session)

        # Verify categories list is now empty
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

        # Verify that entries 3 & 4 have no category association
        entries = api.entry_getall(session=self.session)
        self.assertEqual(len(entries), 2)
        e3, e4 = entries
        self.assertEqual(e3.blob, "ent3")
        self.assertEqual(e3.category_id, None)
        self.assertIsNone(e3.category)
        self.assertEqual(e4.blob, "ent4")
        self.assertEqual(e4.category_id, None)
        self.assertIsNone(e4.category)
