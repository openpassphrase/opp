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


def with_session(function):
    def wrapper(self):
        with self.s.begin():
            function(self)
    return wrapper


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

    def test_items_basic(self):
        # Verify item list empty initially and insert an item
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(items, [])
            item = models.Item(blob="blob", category_id=None, user=self.u)
            api.item_create(self.s, [item])

        # Retrieve and verify inserted item
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].blob, "blob")

        # Update the item
        with self.s.begin():
            item.blob = "new blob"
            api.item_update(self.s, [item])

        # Check the updated item
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].blob, "new blob")
            self.assertEqual(items[0].category_id, None)

        # Update item with valid category
        with self.s.begin():
            category = models.Category(name="blah", user=self.u)
            api.category_create(self.s, [category])
            item.category_id = 1
            api.item_update(self.s, [item])

        # Check the updated item
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].blob, "new blob")
            self.assertEqual(items[0].category_id, 1)
            self.assertIsNotNone(items[0].category)

        # Clean up
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            api.category_delete(self.s, categories, True)

        # Verify clean up successful
        with self.s.begin():
            categories = api.category_getall(self.s, self.u)
            self.assertEqual(len(categories), 0)
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 0)

    def test_items_get_filter(self):
        # Insert several items
        with self.s.begin():
            items = [models.Item(blob="blob0", user=self.u),
                     models.Item(blob="blob1", user=self.u),
                     models.Item(blob="blob2", user=self.u)]
            api.item_create(self.s, items)

        # Retrieve first and last items only
        with self.s.begin():
            ids = [1, 3]
            items = api.item_getall(self.s, self.u, filter_ids=ids)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].blob, "blob0")
            self.assertEqual(items[1].blob, "blob2")

        # Clean up
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            api.item_delete(self.s, items)

        # Verify clean up successful
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 0)

    def test_items_delete_by_id(self):
        # Insert several items
        with self.s.begin():
            items = [models.Item(blob="blob3", user=self.u),
                     models.Item(blob="blob4", user=self.u),
                     models.Item(blob="blob5", user=self.u)]
            api.item_create(self.s, items)

        # Delete first and last items only
        with self.s.begin():
            ids = [1, 3]
            api.item_delete_by_id(self.s, self.u, filter_ids=ids)

        # Check that only the second added item remains
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0].blob, "blob4")

        # Clean up
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            api.item_delete(self.s, items)

        # Verify clean up successful
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 0)

    def test_items_access_by_user(self):
        # Verify item list empty initially and add some items
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(items, [])
            items = [models.Item(blob="item1", user=self.u),
                     models.Item(blob="item2", user=self.u)]
            api.item_create(self.s, items)

        # Retrieve and verify inserted items
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0].blob, "item1")
            self.assertEqual(items[1].blob, "item2")

        # Add another user and retrieve it
        utils.execute("opp-db --config_file %s add-user -uu2 -pp "
                      "--phrase=123456" % self.conf_filepath)
        new_u = api.user_get_by_username(self.s, "u2")
        self.assertEqual(new_u.username, "u2")

        # Attempt to retrieve items with new user
        with self.s.begin():
            new_items = api.item_getall(self.s, new_u)
            self.assertEqual(len(new_items), 0)

        # Clean up
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            api.item_delete(self.s, items)

        # Verify clean up successful
        with self.s.begin():
            items = api.item_getall(self.s, self.u)
            self.assertEqual(len(items), 0)
