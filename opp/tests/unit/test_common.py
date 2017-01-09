import config
import os
import unittest

from opp.common import aescipher, opp_config, utils


class TestUtils(unittest.TestCase):

    def test_extract_path(self):
        env = {'PATH_INFO': "/api/v1/endpoint"}
        path = utils.extract_path(env)
        self.assertEquals(path[0], 'api')
        self.assertEquals(path[1], 'v1')
        self.assertEquals(path[2], 'endpoint')

    def test_extract_query(self):
        env = {'QUERY_STRING': "arg1=123&arg2=456"}
        qs = utils.extract_query(env)
        self.assertEqual(qs['arg1'], ['123'])
        self.assertEqual(qs['arg2'], ['456'])

    def test_qq(self):
        self.assertEqual(utils.qq("123"), "'123'")


class TestAESCipher(unittest.TestCase):

    def test_encrypt_decrypt(self):
        cipher = aescipher.AESCipher("secret passphrase")
        encrypted = cipher.encrypt("My Secret Message")
        decrypted = cipher.decrypt(encrypted)
        self.assertEqual(decrypted, "My Secret Message")


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.file_path = '/tmp/opp.cfg'

    def tearDown(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass

    def test_invalid_path(self):
        # this should not raise any exceptions
        try:
            opp_config.OppConfig('some / invalid / path')
            opp_config.OppConfig(None)
            opp_config.OppConfig()
        except Exception:
            self.fail("Unexpected exception while loading configuration!")

    def test_valid_option(self):
        sql_connect = "sqlite:///:memory:"
        with open(self.file_path, 'w') as f:
            f.write("sql_connect: %s" % utils.qq(sql_connect))
        CONF = opp_config.OppConfig(self.file_path)
        self.assertEqual(CONF['sql_connect'], sql_connect)
        self.assertEqual(CONF['sql_connec'], None)

    def test_invalid_option(self):
        sql_connect = "sqlite:///:memory:"
        with open(self.file_path, 'w') as f:
            f.write("sql_connect: %s" % sql_connect)
        with self.assertRaises(config.ConfigFormatError):
            opp_config.OppConfig(self.file_path)
