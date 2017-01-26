import os
import tempfile
import unittest

from opp.db import api, models
from opp.common import opp_config, utils


class TestDbApiUsers(unittest.TestCase):

    """These tests exercise the top level request/response functionality of
    the backend API.
    Note: All tests share the same DB, so please beware of
    unintended interaction when adding new tests"""
    @classmethod
    def setUpClass(cls):
        cls.test_dir = tempfile.mkdtemp(prefix='opp_')
        cls.conf_filepath = os.path.join(cls.test_dir, 'opp.cfg')
        cls.db_filepath = os.path.join(cls.test_dir, 'test.sqlite')
        cls.connection = ("[DEFAULT]\nsql_connect = sqlite:///%s" %
                          cls.db_filepath)
        with open(cls.conf_filepath, 'w') as conf_file:
            conf_file.write(cls.connection)
            conf_file.flush()
        utils.execute("opp-db --config_file %s init" % cls.conf_filepath)

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
        self.session = api.get_session(conf)

    def tearDown(self):
        self.session.close()

    def test_users_basic(self):
        # Insert and retrieve an user
        user = models.User(username="user", password="pass")
        api.user_create(user, session=self.session)
        user = api.user_get_by_username(user.username, session=self.session)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "user")
        self.assertEqual(user.password, "pass")

        # Update and check the user
        user.username = "new user"
        user.password = "new_pass"
        api.user_update(user, session=self.session)
        new_user = api.user_get_by_id(user.id, session=self.session)
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.username, user.username)
        self.assertEqual(new_user.password, user.password)
        self.assertEqual(new_user.id, user.id)

        # Clean up and verify
        api.user_delete_by_username(user.username, session=self.session)
        user = api.user_get_by_id(user.id, session=self.session)
        self.assertIsNone(user)
