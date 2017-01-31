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
        utils.execute("opp-db --config_file %s add-user -u u -p p" %
                      cls.conf_filepath)

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
        self.c = opp_config.OppConfig(self.conf_filepath)
        self.u = api.user_get_by_username("u", conf=self.c)

    def tearDown(self):
        pass

    def test_items_basic(self):
        # Expect empty item list initially
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(items, [])

        # Insert and retrieve an item
        item = models.Item(blob="blob", category_id=None, user=self.u)
        api.item_create([item], conf=self.c)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 1)

        # Update and check the item
        item.blob = "new blob"
        item.category_id = 999
        api.item_update([item], conf=self.c)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "new blob")
        self.assertEqual(items[0].category_id, 999)

        # Update item with valid category
        category = models.Category(name="blah", user=self.u)
        api.category_create([category], conf=self.c)
        item.category_id = 1
        api.item_update([item], conf=self.c)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "new blob")
        self.assertEqual(items[0].category_id, 1)
        self.assertIsNotNone(items[0].category)

        # Clean up and verify
        categories = api.category_getall(self.u, conf=self.c)
        api.category_delete(categories, True, conf=self.c)
        categories = api.category_getall(self.u, conf=self.c)
        self.assertEqual(len(categories), 0)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 0)

    def test_items_get_filter(self):
        # Insert several items
        items = [models.Item(blob="blob0", user=self.u),
                 models.Item(blob="blob1", user=self.u),
                 models.Item(blob="blob2", user=self.u)]
        api.item_create(items, conf=self.c)

        # Retrieve first and last items only
        ids = [1, 3]
        items = api.item_getall(self.u, filter_ids=ids, conf=self.c)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].blob, "blob0")
        self.assertEqual(items[1].blob, "blob2")

        # Clean up and verify
        items = api.item_getall(self.u, conf=self.c)
        api.item_delete(items, conf=self.c)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 0)

    def test_items_delete_by_id(self):
        # Insert several items
        items = [models.Item(blob="blob3", user=self.u),
                 models.Item(blob="blob4", user=self.u),
                 models.Item(blob="blob5", user=self.u)]
        api.item_create(items, conf=self.c)

        # Delete first and last items only
        ids = [1, 3]
        api.item_delete_by_id(self.u, filter_ids=ids, conf=self.c)

        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].blob, "blob4")

        # Clean up and verify
        items = api.item_getall(self.u, conf=self.c)
        api.item_delete(items, conf=self.c)
        items = api.item_getall(self.u, conf=self.c)
        self.assertEqual(len(items), 0)
