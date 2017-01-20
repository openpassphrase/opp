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

        # Delete the category
        api.category_delete(categories, cascade=False, session=self.session)
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

        # Delete the item
        api.item_delete(items, session=self.session)
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
