from . import BackendApiTest


class UsersApiTests(BackendApiTest):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""

    def test_disallowed_methods_users(self):
        rget = self.client.patch('/users')
        rpat = self.client.patch('/users')
        self.assertEqual(rget.status_code, 405)
        self.assertEqual(rpat.status_code, 405)

    def test_users_cud(self):
        self.hdrs = {"Content-Type": "application/json"}
        path = '/users'

        # Add a user, check for successful response
        data = {'username': "user", 'password': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        # Update the user
        data = {'username': "user", 'current_password': "pass",
                'new_password': "new_pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "success")

        # Delete the user
        data = {'username': "user", 'password': "new_pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")

    def test_users_error_conditions(self):
        self.hdrs = {"Content-Type": "application/json"}
        path = '/users'

        # Try to create user with missing username
        data = {'nousername': "user", 'password': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to create user with empty username
        data = {'username': "", 'password': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to create user with missing password
        data = {'username': "user", 'nopassword': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing password!")

        # Try to create user with empty password
        data = {'username': "user", 'password': ""}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty password!")

        # Try to add the same user twice
        data = {'username': "user", 'password': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "success")

        data = {'username': "user", 'password': "pass"}
        data = self._put(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User already exists!")

        # Try to update user with missing username
        data = {'nousername': "user", 'password': "pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to update user with empty username
        data = {'username': "", 'password': "pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to update user with missing current password
        data = {'username': "user", 'password': "pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing current password!")

        # Try to update user with empty current password
        data = {'username': "user", 'current_password': ""}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty current password!")

        # Try to update user with missing new password
        data = {'username': "user", 'current_password': "pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing new password!")

        # Try to update user with empty new password
        data = {'username': "user", 'current_password': "pass",
                'new_password': ""}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty new password!")

        # Try to update non-existing user
        data = {'username': "nouser", 'current_password': "pass",
                'new_password': "new_pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User doesn't exist!")

        # Try to update user with invalid current password
        data = {'username': "user", 'current_password': "invalid",
                'new_password': "new_pass"}
        data = self._post(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Invalid password!")

        # Try to delete user with missing username
        data = {'nousername': "user", 'password': "pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing username!")

        # Try to delete user with empty username
        data = {'username': "", 'password': "pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty username!")

        # Try to delete user with missing password
        data = {'username': "user", 'nopassword': "pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Missing password!")

        # Try to delete user with empty password
        data = {'username': "user", 'password': ""}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "Empty password!")

        # Try to delete non-existing user
        data = {'username': "nouser", 'password': "pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "error")
        self.assertEqual(data['message'], "User doesn't exist!")

        # Delete the user to clean up
        data = {'username': "user", 'password': "pass"}
        data = self._delete(path, data)
        self.assertEqual(data['result'], "success")
