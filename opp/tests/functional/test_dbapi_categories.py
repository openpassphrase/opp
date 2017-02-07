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

from opp.db import api, models
from opp.common import opp_config, utils


class TestCase(unittest.TestCase):

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
        utils.execute("opp-db --config_file %s add-user -uu -pp "
                      "--phrase=123456" % cls.conf_filepath)

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
        self.s = api.get_scoped_session(conf)
        self.u = api.user_get_by_username(self.s, "u")

    def tearDown(self):
        pass

    def test_categories_basic(self):
        # Verify item list empty initially and insert a category
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(categories, [])
            category = models.Category(name="name", user=self.u)
            api.category_create(self.s, [category])

        # Retrieve and verify inserted category
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 1)
            self.assertEqual(categories[0].name, "name")

        # Update the category
        with self.s.begin():
            category.name = 'new name'
            api.category_update(self.s, [category])

        # Check the updated category
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 1)
            self.assertEqual(categories[0].name, "new name")

        # Clean up
        with self.s.begin():
            api.category_delete(self.s, categories, True)

        # Verify clean up successful
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)

    def test_categories_get_filter(self):
        # Insert several categories
        with self.s.begin():
            categories = [models.Category(name="name0", user=self.u),
                          models.Category(name="name1", user=self.u),
                          models.Category(name="name2", user=self.u)]
            api.category_create(self.s, categories)

        # Retrieve first and last categories only
        with self.s.begin():
            ids = [1, 3]
            categories = api.category_getall(self.s, self.u, filter_ids=ids)
            self.assertEqual(len(categories), 2)
            self.assertEqual(categories[0].name, "name0")
            self.assertEqual(categories[1].name, "name2")

        # Clean up
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            api.category_delete(self.s, categories, True)

        # Verify clean up successful
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)

    def test_categories_delete_by_id(self):
        # Insert several categories
        with self.s.begin():
            categories = [models.Category(name="name3", user=self.u),
                          models.Category(name="name4", user=self.u),
                          models.Category(name="name5", user=self.u)]
            api.category_create(self.s, categories)

        # Delete first and last categories only
        with self.s.begin():
            ids = [1, 3]
            api.category_delete_by_id(self.s, self.u, ids, cascade=False)

        # Verify only second added category remains
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 1)
            self.assertEqual(categories[0].name, "name4")

        # Clean up
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            api.category_delete(self.s, categories, True)

        # Verify clean up successful
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)

    def test_categories_delete_cascade(self):
        # Create two categories
        with self.s.begin():
            categories = [models.Category(name="cat1", user=self.u),
                          models.Category(name="cat2", user=self.u)]
            api.category_create(self.s, categories)

        # Verify created categories
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 2)
            self.assertEqual(categories[0].name, "cat1")
            self.assertEqual(categories[1].name, "cat2")

        # Create 4 items
        with self.s.begin():
            items = [models.Item(blob="item1", category_id=1, user=self.u),
                     models.Item(blob="item2", category_id=1, user=self.u),
                     models.Item(blob="item3", category_id=2, user=self.u),
                     models.Item(blob="item4", category_id=2, user=self.u)]
            api.item_create(self.s, items)

        # Verify created items
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
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
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            api.category_delete(self.s, categories[:1], cascade=True)

        # Verify only 1 category remains
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 1)
            self.assertEqual(categories[0].name, "cat2")

        # Verify items 1 & 2 were deleted through cascade action
        # and that items 3 & 4 remain unchanged
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
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
        with self.s.begin():
            api.category_delete(self.s, categories, cascade=False)

        # Verify categories list is now empty
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)

        # Verify that items 3 & 4 have no category association
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 2)
            i3, i4 = items
            self.assertEqual(i3.blob, "item3")
            self.assertEqual(i3.category_id, None)
            self.assertIsNone(i3.category)
            self.assertEqual(i4.blob, "item4")
            self.assertEqual(i4.category_id, None)
            self.assertIsNone(i4.category)

        # Remove remaining category
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            api.category_delete(self.s, categories, True)

        # Verify categories list is now empty
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)

        # Make sure items were NOT deleted despite cascade=True
        # because they have no category association
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 2)
            i3, i4 = items
            self.assertEqual(i3.blob, "item3")
            self.assertEqual(i3.category_id, None)
            self.assertIsNone(i3.category)
            self.assertEqual(i4.blob, "item4")
            self.assertEqual(i4.category_id, None)
            self.assertIsNone(i4.category)

        # Clean up remaining items
        with self.s.begin():
            api.item_delete(self.s, items)

        # Verify clean up successful
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 0)
