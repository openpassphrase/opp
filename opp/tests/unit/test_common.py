import unittest

from opp.common import aescipher
from opp.common import utils


class TestCommonUtils(unittest.TestCase):

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