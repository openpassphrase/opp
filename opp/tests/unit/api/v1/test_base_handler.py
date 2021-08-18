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

from flask import Flask
from opp.api.v1 import base_handler as bh
from opp.common import aescipher as ac


class TestBaseResponseHandler(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        self.ctx = app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def assertRaisesWithMsg(self, msg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFail()
        except Exception as e:
            self.assertEqual(e.error, msg)

    @mock.patch('flask.request')
    def test_check_payload_empty_ok(self, request):
        request.get_json.return_value = {}
        handler = bh.BaseResponseHandler(request, None, None)
        payload = handler._check_payload()
        self.assertEqual(payload, [])

    @mock.patch('flask.request')
    def test_check_payload_empty_not_ok(self, request):
        request.get_json.return_value = {}
        handler = bh.BaseResponseHandler(request, None, None)
        self.assertRaisesWithMsg("Missing payload!",
                                 handler._check_payload, True)

    @mock.patch('flask.request')
    def test_check_payload_none(self, request):
        request.get_json.return_value = None
        handler = bh.BaseResponseHandler(request, None, None)
        self.assertRaisesWithMsg("Missing payload!",
                                 handler._check_payload, True)

    @mock.patch('flask.request')
    def test_check_payload_objects(self, request):
        payload = {'obj': {'name': "value"},
                   'list_obj': [1, 2, 3]}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
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

    @mock.patch('flask.request')
    def test_check_payload_object_missing_not_required(self, request):
        payload = {'obj': {'name': "value"}}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
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

    @mock.patch('flask.request')
    def test_check_payload_object_missing_required(self, request):
        payload = {'obj': {'name': "value"}}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
        check_dict = [{'name': "obj",
                       'is_list': False,
                       'required': True},
                      {'name': "list_obj",
                       'is_list': True,
                       'required': True}]
        self.assertRaisesWithMsg("Required payload object "
                                 "'list_obj' is missing!",
                                 handler._check_payload, check_dict)

    @mock.patch('flask.request')
    def test_check_payload_object_expect_list(self, request):
        payload = {'obj': {'name': "value"}}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
        check_dict = [{'name': "obj", 'is_list': True, 'required': True}]
        self.assertRaisesWithMsg("'obj' object should be in list form!",
                                 handler._check_payload, check_dict)

    @mock.patch('flask.request')
    def test_check_payload_object_not_list(self, request):
        payload = {'obj': [1, 2, 3]}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
        check_dict = [{'name': "obj", 'is_list': False, 'required': True}]
        self.assertRaisesWithMsg("'obj' object should not be in list form!",
                                 handler._check_payload, check_dict)

    @mock.patch('flask.request')
    def test_respond_missing_phrase(self, request):
        request.headers = {}
        handler = bh.BaseResponseHandler(request, None, None)
        self.assertRaisesWithMsg("Passphrase header missing!",
                                 handler.respond)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    def test_respond_bad_phrase(self, request, cipher, user):
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "NOTOK"
        handler = bh.BaseResponseHandler(request, user, None)
        self.assertRaisesWithMsg("Incorrect passphrase supplied!",
                                 handler.respond)

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_get')
    def test_respond_get(self, func, session, request, cipher, user):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_put')
    def test_respond_put(self, func, session, request, cipher, user):
        request.method = "PUT"
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_post')
    def test_respond_post(self, func, session, request, cipher, user):
        request.method = "POST"
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_delete')
    def test_respond_delete(self, func, session, request, cipher, user):
        request.method = "DELETE"
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    def test_respond_bad_verb(self, session, request, cipher, user):
        request.method = "BAD"
        cipher.return_value = "OK"
        handler = bh.BaseResponseHandler(request, user, session)
        self.assertRaisesWithMsg("Method not supported!",
                                 handler.respond, require_phrase=False)
