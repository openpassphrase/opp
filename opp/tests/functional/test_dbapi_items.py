import os
import tempfile
import unittest

from opp.db import api, models
from opp.common import opp_config, utils


class TestDbApiItems(unittest.TestCase):

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
        super(TestDbApiItems, self).setUp()
        conf = opp_config.OppConfig(self.conf_filepath)
        self.session = api.get_session(conf)

    def tearDown(self):
        self.session.close()
        super(TestDbApiItems, self).tearDown()

    def test_items_basic(self):
        # Expect empty item list initially
        items = api.item_getall(session=self.session)
        self.assertEqual(items, [])

        # Insert and retrieve an item
        item = models.Item(blob="blob", category_id=None)
        api.item_create([item], session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 1)

        # Update and check the item
        item.blob = "new blob"
        item.category_id = 999
        api.item_update([item], session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "new blob")
        self.assertEqual(items[0].category_id, 999)

        # Update item with valid category
        category = models.Category(name="blah")
        api.category_create([category], session=self.session)
        item.category_id = 1
        api.item_update([item], session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "new blob")
        self.assertEqual(items[0].category_id, 1)
        self.assertIsNotNone(items[0].category)

        # Clean up and verify
        categories = api.category_getall(session=self.session)
        api.category_delete(categories, True, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 0)

    def test_items_get_filter(self):
        # Insert several items
        items = [models.Item(blob="blob0"),
                 models.Item(blob="blob1"),
                 models.Item(blob="blob2")]
        api.item_create(items, session=self.session)

        # Retrieve first and last items only
        ids = [1, 3]
        items = api.item_getall(filter_ids=ids, session=self.session)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].blob, "blob0")
        self.assertEqual(items[1].blob, "blob2")

        # Clean up and verify
        items = api.item_getall(session=self.session)
        api.item_delete(items, session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 0)

    def test_items_delete_by_id(self):
        # Insert several items
        items = [models.Item(blob="blob3"),
                 models.Item(blob="blob4"),
                 models.Item(blob="blob5")]
        api.item_create(items, session=self.session)

        # Delete first and last items only
        ids = [1, 3]
        api.item_delete_by_id(filter_ids=ids, session=self.session)

        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "blob4")

        # Clean up and verify
        items = api.item_getall(session=self.session)
        api.item_delete(items, session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 0)
