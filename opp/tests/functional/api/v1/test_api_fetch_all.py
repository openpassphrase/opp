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

from . import BackendApiTest


class TestApiFetchAll(BackendApiTest):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    def test_disallowed_methods_fetch_all(self):
        rput = self.client.put('/v1/fetchall')
        rpos = self.client.post('/v1/fetchall')
        rdel = self.client.delete('/v1/fetchall')
        rpat = self.client.patch('/v1/fetchall')
        self.assertEqual(rput.status_code, 405)
        self.assertEqual(rpos.status_code, 405)
        self.assertEqual(rdel.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_fetch_all_get(self):
        self.hdrs = {'x-opp-phrase': "123",
                     'x-opp-jwt': self.jwt,
                     'Content-Type': "application/json"}
        path = '/v1/fetchall'
        cpath = '/v1/categories'
        ipath = '/v1/items'

        # Request fetchall, expect empty list initially
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(data['categories'], [])

        # Add 2 categories, check for successful response
        data = {'payload': ["cat1", "cat2"]}
        data = self._put(cpath, data)
        self.assertEqual(data['result'], "success")

        # Add 6 items, check for successful response
        data = {'payload':
                [{"name": "i1", "category_id": 1},
                 {"name": "i2", "category_id": 1},
                 {"name": "i3", "category_id": 2},
                 {"name": "i4", "category_id": 2},
                 {"name": "i5"},
                 {"name": "i6"}]}
        data = self._put(ipath, data)
        self.assertEqual(data['result'], "success")

        # Perform fetchall and check
        data = self._get(path)
        self.assertEqual(data['result'], "success")
        self.assertEqual(len(data['categories']), 3)

        c1, c2, c3 = data['categories']

        self.assertEqual(len(c1['cat1']), 2)
        self.assertEqual(len(c2['cat2']), 2)
        self.assertEqual(len(c3['default']), 2)

        self.assertEqual(c1['cat1'][0]['name'], "i1")
        self.assertEqual(c1['cat1'][1]['name'], "i2")

        self.assertEqual(c2['cat2'][0]['name'], "i3")
        self.assertEqual(c2['cat2'][1]['name'], "i4")

        self.assertEqual(c3['default'][0]['name'], "i5")
        self.assertEqual(c3['default'][1]['name'], "i6")
