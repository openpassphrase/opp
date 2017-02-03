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

from opp.api.v1 import base_handler as bh


class TestBaseResponseHandler(unittest.TestCase):

    @mock.patch('flask.request')
    def test_check_payload_empty(self, request):
        request.get_json.return_value = {}
        handler = bh.BaseResponseHandler(request, None, None)
        payload, error = handler._check_payload()
        self.assertEqual(payload, [])
        self.assertEqual(error, None)

    @mock.patch('flask.request')
    def test_check_payload_none(self, request):
        request.get_json.return_value = None
        handler = bh.BaseResponseHandler(request, None, None)
        payload, error = handler._check_payload(True)
        self.assertEqual(payload, None)
        self.assertEqual(error, {'result': "error",
                                 'message': "Missing payload!"})

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
        payload_objects, error = handler._check_payload(check_dict)
        self.assertNotEqual(payload_objects, None)
        self.assertIsNone(error)
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
                       'required': False}]
        payload_objects, error = handler._check_payload(check_dict)
        self.assertNotEqual(payload_objects, None)
        self.assertIsNone(error)
        self.assertEqual(len(payload_objects), 1)
        self.assertEqual(payload_objects[0]['name'], "value")

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
        payload_objects, error = handler._check_payload(check_dict)
        self.assertIsNone(payload_objects)
        self.assertIsNotNone(error)
        self.assertEqual(error['result'], "error")
        self.assertEqual(error['message'], ("Required payload object "
                                            "'list_obj' is missing!"))

    @mock.patch('flask.request')
    def test_check_payload_object_expect_list(self, request):
        payload = {'obj': {'name': "value"}}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
        check_dict = [{'name': "obj", 'is_list': True, 'required': True}]
        payload_objects, error = handler._check_payload(check_dict)
        self.assertIsNone(payload_objects)
        self.assertIsNotNone(error)
        self.assertEqual(error['result'], "error")
        self.assertEqual(error['message'], ("'obj' object should be "
                                            "in list form!"))

    @mock.patch('flask.request')
    def test_check_payload_object_not_list(self, request):
        payload = {'obj': [1, 2, 3]}
        request.get_json.return_value = payload
        handler = bh.BaseResponseHandler(request, None, None)
        check_dict = [{'name': "obj", 'is_list': False, 'required': True}]
        payload_objects, error = handler._check_payload(check_dict)
        self.assertIsNone(payload_objects)
        self.assertIsNotNone(error)
        self.assertEqual(error['result'], "error")
        self.assertEqual(error['message'], ("'obj' object should not "
                                            "be in list form!"))

    @mock.patch('flask.request')
    def test_respond_missing_phrase(self, request):
        request.headers = {}
        handler = bh.BaseResponseHandler(request, None, None)
        self.assertEqual(handler.respond(),
                         {'result': "error",
                         'message': "Passphrase header missing!"})

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_get')
    def test_respond_get(self, func, session, request):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_put')
    def test_respond_put(self, func, session, request):
        request.method = "PUT"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_post')
    def test_respond_post(self, func, session, request):
        request.method = "POST"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(bh.BaseResponseHandler, '_do_delete')
    def test_respond_delete(self, func, session, request):
        request.method = "DELETE"
        request.headers = {'x-opp-phrase': "123"}
        handler = bh.BaseResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func)

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    def test_respond_bad_verb(self, session, request):
        request.method = "BAD"
        handler = bh.BaseResponseHandler(request, None, session)
        response = handler.respond(require_phrase=False)
        expected = {'result': "error", 'message': "Method not supported!"}
        self.assertEqual(response, expected)


class TestErrorResponseHandler(unittest.TestCase):

    def test_respond(self):
        handler = bh.ErrorResponseHandler("some error msg")
        response = handler.respond()
        expected = {'message': 'some error msg', 'result': 'error'}
        self.assertEqual(response, expected)
