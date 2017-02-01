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

from opp.api.v1 import categories as api


class TestResponseHandler(unittest.TestCase):

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(api.ResponseHandler, '_do_get')
    def test_respond_get(self, func, session, request):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(api.ResponseHandler, '_do_put')
    def test_respond_put(self, func, session, request):
        request.method = "PUT"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, "123")

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(api.ResponseHandler, '_do_post')
    def test_respond_post(self, func, session, request):
        request.method = "POST"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func, '123')

    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(api.ResponseHandler, '_do_delete')
    def test_respond_delete(self, func, session, request):
        request.method = "DELETE"
        request.headers = {'x-opp-phrase': "123"}
        handler = api.ResponseHandler(request, None, session)
        handler.respond()
        self._check_called(func)
