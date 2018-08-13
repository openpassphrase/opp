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


class TestCase(BackendApiTest):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    def test_disallowed_methods_user(self):
        rget = self.client.get('/v1/user')
        rpat = self.client.patch('/v1/user')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_user_crud(self):
        self.hdrs = {'Content-Type': "application/json"}
        path = '/v1/user'

        # Add user, check for successful response
        data = {"username": "test_user1", "password": "test_password1",
                "phrase": "123456"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Update user, check for successful response
        data = {"username": "test_user1", "password": "test_password1",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Delete user, check for successfull response
        data = {"username": "test_user2", "password": "test_password2"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

    def test_user_error_conditions(self):
        self.hdrs = {'Content-Type': "application/json"}
        path = '/v1/user'

        # Try to add a user without username
        data = {"username": "          ", "password": "test_password1",
                "phrase": "123456"}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'], "Input 'username' parameter is empty!")

        # Try to add a user without password
        data = {"username": "test_user1", "password": "              ",
                "phrase": "123456"}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'], "Input 'password' parameter is empty!")

        # Try to add a user without phrase
        data = {"username": "test_user1", "password": "test_password1",
                "phrase": "      "}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'], "Input 'phrase' parameter is empty!")

        # Try to add a user with invalid phrase
        data = {"username": "test_user1", "password": "test_password1",
                "phrase": "12345"}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'],
                         "Passphrase must be at least 6 characters long!")

        # Add a user
        data = {"username": "test_user1", "password": "test_password1",
                "phrase": "123456"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Try to add existing user
        data = {"username": "test_user1", "password": "test_password1",
                "phrase": "123456"}
        data = self._put(path, data, 400)
        self.assertEqual(data['error'], "User already exists!")

        # Try to update user without username
        data = {"username": "          ", "password": "test_password1",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Input 'username' parameter is empty!")

        # Try to update user without password
        data = {"username": "test_user1", "password": "              ",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Input 'password' parameter is empty!")

        # Try to update user without new user data
        data = {"username": "test_user1", "password": "test_password1",
                "new_username": "          ", "new_password": "              "}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "at least one of: [--new_username,"
                                        " --new_password] is required!")

        # Try to update non-existing user
        data = {"username": "test_user2", "password": "test_password1",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "User does not exist!")

        # Try to update user without password
        data = {"username": "test_user1", "password": "test_password2",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Incorrect password supplied!")

        # Add a second user
        data = {"username": "test_user2", "password": "test_password2",
                "phrase": "123456"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Try to update first user with existing username
        data = {"username": "test_user1", "password": "test_password1",
                "new_username": "test_user2", "new_password": "test_password2"}
        data = self._post(path, data, 400)
        self.assertEqual(data['error'], "Username: 'test_user2' "
                                        "already exists!")

        # Clean up second user
        data = {"username": "test_user2", "password": "test_password2"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

        # Try to delete non-existing user
        data = {"username": "test_user2", "password": "test_password2"}
        data = self._delete(path, data, 400)
        self.assertEqual(data['error'], "User does not exist!")

        # Try to delete user without username
        data = {"username": "          ", "password": "test_password2"}
        data = self._delete(path, data, 400)
        self.assertEqual(data['error'], "Input 'username' parameter is empty!")

        # Try to delete user without password
        data = {"username": "test_user1", "password": "              "}
        data = self._delete(path, data, 400)
        self.assertEqual(data['error'], "Input 'password' parameter is empty!")

        # Try to delete user without password
        data = {"username": "test_user1", "password": "test_password2"}
        data = self._delete(path, data, 400)
        self.assertEqual(data['error'], "Incorrect password supplied!")
