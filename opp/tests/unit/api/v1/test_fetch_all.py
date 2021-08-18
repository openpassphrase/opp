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
from opp.api.v1 import fetch_all as api
from opp.common import aescipher as ac


class TestResponseHandler(unittest.TestCase):

    def setUp(self):
        app = Flask(__name__)
        self.ctx = app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def _check_called(self, func_name, *exp_args, **exp_kwargs):
        func_name.assert_called_once_with(*exp_args, **exp_kwargs)

    @mock.patch('opp.db.models.User')
    @mock.patch.object(ac.AESCipher, 'decrypt')
    @mock.patch('flask.request')
    @mock.patch('sqlalchemy.orm.scoped_session')
    @mock.patch.object(api.ResponseHandler, '_do_get')
    def test_respond_get(self, func, session, request, cipher, user):
        request.method = "GET"
        request.headers = {'x-opp-phrase': "123"}
        cipher.return_value = "OK"
        handler = api.ResponseHandler(request, user, session)
        handler.respond()
        self._check_called(func, "123")
