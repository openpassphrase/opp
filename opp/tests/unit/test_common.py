# -*- coding: utf-8 -*-

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

from six.moves import configparser
import os
import unittest

from opp.common import aescipher, opp_config


class TestUtils(unittest.TestCase):

    def test_checkpw(self):
        pass

    def test_hashpw(self):
        pass


class TestAESCipher(unittest.TestCase):

    def test_encrypt_decrypt(self):
        cipher = aescipher.AESCipher("secret passphrase")
        encrypted = cipher.encrypt("My Secret Message")
        decrypted = cipher.decrypt(encrypted)
        self.assertEqual(decrypted, "My Secret Message")

    def test_encrypt_decrypt_unicode_data(self):
        cipher = aescipher.AESCipher("secret passphrase")
        encrypted = cipher.encrypt(u"Привет Мир!")
        decrypted = cipher.decrypt(encrypted)
        self.assertEqual(decrypted, u"Привет Мир!")


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

    def test_missing_section(self):
        with open(self.file_path, 'w') as f:
            f.write("db_connect = blah")
        with self.assertRaises(configparser.MissingSectionHeaderError):
            opp_config.OppConfig(self.file_path)

    def test_valid_option(self):
        db_connect = "sqlite:///:memory:"
        with open(self.file_path, 'w') as f:
            f.write("[DEFAULT]\n")
            f.write("db_connect = %s" % db_connect)
        CONF = opp_config.OppConfig(self.file_path)
        self.assertEqual(CONF['db_connect'], db_connect)

    def test_empty_option(self):
        CONF = opp_config.OppConfig()
        self.assertIsNone(CONF['test_option'])
