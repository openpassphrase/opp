import os
import tempfile
import unittest

from opp.db import api, models
from opp.common import opp_config, utils


class TestDbApiCategories(unittest.TestCase):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        cls.connection = ("sql_connect: 'sqlite:///%s'" % cls.db_filepath)
        with open(cls.conf_filepath, 'wb') as conf_file:
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
        self.session = api.get_session(conf)

    def tearDown(self):
        self.session.close()

    def test_categories_basic(self):
        # Expect empty category list initially
        categories = api.category_getall(session=self.session)
        self.assertEqual(categories, [])

        # Insert and retrieve a category
        category = models.Category(name="name")
        api.category_create([category], session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)

        # Update and check the category
        category.name = 'new name'
        api.category_update([category], session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "new name")

        # Clean up and verify
        api.category_delete(categories, True, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

    def test_categories_get_filter(self):
        # Insert several categories
        categories = [models.Category(name="name0"),
                      models.Category(name="name1"),
                      models.Category(name="name2")]
        api.category_create(categories, session=self.session)

        # Retrieve first and last categories only
        ids = [1, 3]
        categories = api.category_getall(filter_ids=ids, session=self.session)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "name0")
        self.assertEqual(categories[1].name, "name2")

        # Clean up and verify
        categories = api.category_getall(session=self.session)
        api.category_delete(categories, True, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

    def test_categories_delete_by_id(self):
        # Insert several categories
        categories = [models.Category(name="name3"),
                      models.Category(name="name4"),
                      models.Category(name="name5")]
        api.category_create(categories, session=self.session)

        # Delete first and last categories only
        ids = [1, 3]
        api.category_delete_by_id(ids, cascade=False, session=self.session)

        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "name4")

        # Clean up and verify
        categories = api.category_getall(session=self.session)
        api.category_delete(categories, True, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

    def test_categories_delete_cascade(self):
        # Insert categories
        categories = [models.Category(name="cat1"),
                      models.Category(name="cat2")]
        api.category_create(categories, session=self.session)

        # Verify categories
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 2)
        self.assertEqual(categories[0].name, "cat1")
        self.assertEqual(categories[1].name, "cat2")

        # Insert items
        items = [models.Item(blob="item1", category_id=1),
                 models.Item(blob="item2", category_id=1),
                 models.Item(blob="item3", category_id=2),
                 models.Item(blob="item4", category_id=2)]
        api.item_create(items, session=self.session)

        # Verify items
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 4)

        i1, i2, i3, i4 = items

        self.assertEqual(i1.blob, "item1")
        self.assertEqual(i1.category_id, 1)
        self.assertIsNotNone(i1.category)
        self.assertEqual(i1.category.id, 1)

        self.assertEqual(i2.blob, "item2")
        self.assertEqual(i2.category_id, 1)
        self.assertIsNotNone(i2.category)
        self.assertEqual(i1.category.id, 1)

        self.assertEqual(i3.blob, "item3")
        self.assertEqual(i3.category_id, 2)
        self.assertIsNotNone(i3.category)
        self.assertEqual(i3.category.id, 2)

        self.assertEqual(i4.blob, "item4")
        self.assertEqual(i4.category_id, 2)
        self.assertIsNotNone(i4.category)
        self.assertEqual(i4.category.id, 2)

        # Delete category 1 with cascade
        api.category_delete(categories[:1], cascade=True,
                            session=self.session)

        # Verify only 1 category remains
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].name, "cat2")

        # Verify items 1 & 2 were deleted through cascade action
        # and that items 3 & 4 remain unchanged
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 2)
        i3, i4 = items
        self.assertEqual(i3.blob, "item3")
        self.assertEqual(i3.category_id, 2)
        self.assertIsNotNone(i3.category)
        self.assertEqual(i3.category.id, 2)
        self.assertEqual(i4.blob, "item4")
        self.assertEqual(i4.category_id, 2)
        self.assertIsNotNone(i4.category)
        self.assertEqual(i4.category.id, 2)

        # Delete category 2 without cascade
        api.category_delete(categories, cascade=False,
                            session=self.session)

        # Verify categories list is now empty
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

        # Verify that items 3 & 4 have no category association
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 2)
        i3, i4 = items
        self.assertEqual(i3.blob, "item3")
        self.assertEqual(i3.category_id, None)
        self.assertIsNone(i3.category)
        self.assertEqual(i4.blob, "item4")
        self.assertEqual(i4.category_id, None)
        self.assertIsNone(i4.category)

        # Clean up and verify
        categories = api.category_getall(session=self.session)
        api.category_delete(categories, True, session=self.session)
        categories = api.category_getall(session=self.session)
        self.assertEqual(len(categories), 0)

        items = api.item_getall(session=self.session)
        api.item_delete(items, session=self.session)
        items = api.item_getall(session=self.session)
        self.assertEqual(len(items), 0)
