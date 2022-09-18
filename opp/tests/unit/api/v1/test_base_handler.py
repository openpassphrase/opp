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

import mock
import unittest

from mock_request import MockRequest

from opp.api.v1 import base_handler as bh
from opp.common import aescipher as ac


class TestBaseResponseHandler(unittest.TestCase):

    def assertRaisesWithMsg(self, msg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFail()
        except Exception as e:
            self.assertEqual(e.error, msg)

    def test_check_payload_empty_ok(self):
        handler = bh.BaseResponseHandler(MockRequest('', {}, {}), None, None)
        payload = handler._check_payload()
        self.assertEqual(payload, [])

    def test_check_payload_empty_not_ok(self):
        handler = bh.BaseResponseHandler(MockRequest('', {}, None), None, None)
        self.assertRaisesWithMsg("Missing payload!",
                                 handler._check_payload, True)

    def test_check_payload_none(self):
        handler = bh.BaseResponseHandler(MockRequest('', {}, None), None, None)
        self.assertRaisesWithMsg("Missing payload!",
                                 handler._check_payload, True)

    def test_check_payload_objects(self):
        payload = {'obj': {'name': "value"},
                   'list_obj': [1, 2, 3]}
        handler = bh.BaseResponseHandler(MockRequest('', {}, payload), None, None)
        check_dict = [{'name': "obj",
                       'is_list': False,
                       'required': True},
                      {'name': "list_obj",
                       'is_list': True,
                       'required': False}]
        payload_objects = handler._check_payload(check_dict)
        self.assertNotEqual(payload_objects, None)
        self.assertEqual(len(payload_objects), 2)
        obj, list_obj = payload_objects
        self.assertEqual(obj['name'], "value")
        self.assertEqual(len(list_obj), 3)

    def test_check_payload_object_missing_not_required(self):
        payload = {'obj': {'name': "value"}}
        handler = bh.BaseResponseHandler(MockRequest('', {}, payload), None, None)
        check_dict = [{'name': "obj",
                       'is_list': False,
                       'required': True},
                      {'name': "list_obj",
                       'is_list': True,
                       'required': False},
                      {'name': "obj2",
                       'is_list': False,
                       'required': False}]
        payload_objects = handler._check_payload(check_dict)
        self.assertNotEqual(payload_objects, None)
        self.assertEqual(len(payload_objects), 3)
        self.assertEqual(payload_objects[0]['name'], "value")
        self.assertEqual(payload_objects[1], [])
        self.assertEqual(payload_objects[2], {})

    def test_check_payload_object_missing_required(self):
        payload = {'obj': {'name': "value"}}
        handler = bh.BaseResponseHandler(MockRequest('', {}, payload), None, None)
        check_dict = [{'name': "obj",
                       'is_list': False,
                       'required': True},
                      {'name': "list_obj",
                       'is_list': True,
                       'required': True}]
        self.assertRaisesWithMsg("Required payload object "
                                 "'list_obj' is missing!",
                                 handler._check_payload, check_dict)

    def test_check_payload_object_expect_list(self):
        payload = {'obj': {'name': "value"}}
        handler = bh.BaseResponseHandler(MockRequest('', {}, payload), None, None)
        check_dict = [{'name': "obj", 'is_list': True, 'required': True}]
        self.assertRaisesWithMsg("'obj' object should be in list form!",
                                 handler._check_payload, check_dict)

    def test_check_payload_object_not_list(self):
        payload = {'obj': [1, 2, 3]}
        handler = bh.BaseResponseHandler(MockRequest('', {}, payload), None, None)
        check_dict = [{'name': "obj", 'is_list': False, 'required': True}]
        self.assertRaisesWithMsg("'obj' object should not be in list form!",
                                 handler._check_payload, check_dict)

    def test_respond_missing_phrase(self):
        handler = bh.BaseResponseHandler(MockRequest('', {}, None), None, None)
        self.assertRaisesWithMsg("Passphrase header missing!",
                                 handler.respond)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    def test_respond_bad_phrase(self, cipher, user):
        cipher.return_value = "NOTOK"
        headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(MockRequest('', headers, None), user, None)
        self.assertRaisesWithMsg("Incorrect passphrase supplied!",
                                 handler.respond)

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_get')
    def test_respond_get(self, func, session, cipher, user):
        request = MockRequest('GET', {'x-opp-phrase': "123"}, None)
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_put')
    def test_respond_put(self, func, session, cipher, user):
        request = MockRequest('PUT', {'x-opp-phrase': "123"}, None)
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_post')
    def test_respond_post(self, func, session, cipher, user):
        request = MockRequest('POST', {'x-opp-phrase': "123"}, None)
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_delete')
    def test_respond_delete(self, func, session, cipher, user):
        request = MockRequest('DELETE', {'x-opp-phrase': "123"}, None)
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('sqlalchemy.orm.scoped_session')
    def test_respond_bad_verb(self, session, cipher, user):
        request = MockRequest('BAD', {'x-opp-phrase': "123"}, None)
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        self.assertRaisesWithMsg("Method not supported!",
                                 handler.respond, require_phrase=False)
