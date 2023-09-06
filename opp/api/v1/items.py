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

from random import shuffle
import re
from xkcdpass import xkcd_password as xp

from opp.api.v1 import base_handler as bh
from opp.common import aescipher, opp_config
from opp.db import api, models


CONFIG = opp_config.OppConfig()


class ResponseHandler(bh.BaseResponseHandler):
    """
    Response handler for the `items` endpoint.
    """

    def _parse_or_set_empty(self, row, key, none_if_empty=False):
        """
        Retrieve a value from `row` by `key`.

        :param none_if_empty: specifies to return either None or empty
        string if key is not found in object.

        :returns: extracted value if found, None or "" otherwise
        """
        try:
            value = row[key]
        except KeyError:
            if none_if_empty:
                return None
            else:
                return ""
        if not none_if_empty and value is None:
            return ""
        return value

    def _get_words(self, options):
        """Locate a word file and parse it to get a list of words from which
        xkcdpass module will randomly choose a passphrase. The word file may
        be specified in the configuration file specific to a particular
        deployment. Otherwise the algorithm will try to locate a standard
        word file from well known locations.

        :param options: contains options for xkcdpass configuring the type of
        words to include.

        :returns: list of words
        """
        wordfile = CONFIG['wordfile'] or xp.locate_wordfile()

        try:
            min_length = options['min_length']
        except (TypeError, KeyError):
            min_length = 5
        try:
            max_length = options['max_length']
        except (TypeError, KeyError):
            max_length = 15
        try:
            valid_chars = options['valid_chars']
        except (TypeError, KeyError):
            valid_chars = "."

        # Sanity validation
        msg = "Invalid password generation options!"

        if min_length < 1 or min_length > 15:
            desc = ("For sanity's sake, minimum length must be "
                    "a positive number less than or equal to 15.")
            raise bh.OppError(msg, desc)

        if max_length < 5 or max_length > 20:
            desc = ("For sanity's sake, maximum length must"
                    " be a number between 5 and 20.")
            raise bh.OppError(msg, desc)

        if min_length > max_length:
            desc = "Minimum length cannot be larger than maximum length."
            raise bh.OppError(msg, desc)

        try:
            return xp.generate_wordlist(wordfile=wordfile,
                                        min_length=min_length,
                                        max_length=max_length,
                                        valid_chars=valid_chars)
        except Exception:
            raise bh.OppError("Exception during password generation!",
                              None, 500)

    def _gen_pwd(self, words, options):
        """
        Wrapper function around xkcdpass password generation logic

        :param words: list of words to use for password generation
        :param options: additional password generation constraints

        :returns: generated multi-word password
        """
        try:
            numwords = options['numwords']
        except (TypeError, KeyError):
            numwords = 4

        # Sanity validation
        if numwords < 1 or numwords > 20:
            msg = "Invalid password generation options!"
            desc = ("For sanity's sake, numwords must be a "
                    "positive number less than or equal to 20.")
            raise bh.OppError(msg, desc)

        try:
            tries = 50
            while True:
                phrase = xp.generate_xkcdpassword(words,
                                                  numwords=numwords,
                                                  interactive=False,
                                                  acrostic=False,
                                                  random_delimiters=True,
                                                  case='random')
                if self._validate_pwd(phrase):
                    break
                tries -= 1
                if not tries:
                    raise bh.OppError("Cannot generate compliant password after 50 tries, giving up!", None, 500)
            phrase = list(phrase)
            shuffle(phrase)
            return ''.join(phrase)
        except Exception:
            raise bh.OppError("Exception during password generation!", None, 500)

    def _validate_pwd(self, s):
        return re.search('[a-z]', s) and re.search('[A-Z]', s) and re.search('[!@#$%^&*()-+=\\_]', s)

    def make_item(self, row, cipher, password, item_id=None):
        """
        Extract various item data from the request and encrypt it

        :param row: item object parsed from JSON request
        :param cipher: encryption cipher
        :param password: if specified, ignore the `password` field in
        in the item object and instead use this auto-generated password.
        :param item_id: should be specified for item update operations,
        None otherwise.

        :returns Item ORM model for insertion into the database
        """
        # Extract various item data into a list
        name = self._parse_or_set_empty(row, 'name')
        url = self._parse_or_set_empty(row, 'url')
        account = self._parse_or_set_empty(row, 'account')
        username = self._parse_or_set_empty(row, 'username')
        password = password or self._parse_or_set_empty(row, 'password')
        blob = self._parse_or_set_empty(row, 'blob')
        category_id = self._parse_or_set_empty(row, 'category_id', True)

        try:
            return models.Item(id=item_id,
                               name=cipher.encrypt(name),
                               url=cipher.encrypt(url),
                               account=cipher.encrypt(account),
                               username=cipher.encrypt(username),
                               password=cipher.encrypt(password),
                               blob=cipher.encrypt(blob),
                               category_id=category_id,
                               user=self.user)
        except (AttributeError, TypeError):
            raise bh.OppError("Invalid item data in list!")

    def _do_get(self, phrase):
        """
        Fetch all user's items.

        :param phrase: decryption passphrase

        :returns: success result along with decrypted items array
        """
        response = []
        cipher = aescipher.AESCipher(phrase)
        try:
            items = api.item_getall(self.session, self.user)
            for item in items:
                response.append(item.extract(cipher))
        except UnicodeDecodeError:
            raise bh.OppError("Unable to decrypt data!")
        except Exception:
            raise bh.OppError("Unable to fetch items from the database!")
        return {'result': 'success', 'items': response}

    def _do_put(self, phrase):
        """
        Create a list of items, given an array of item parameters, with
        option to specify auto-generation of common or unique passwords
        for each item.

        :param phrase: decryption passphrase

        :returns: success result along with array of newly created items
        """
        payload_dicts = [{'name': "items",
                          'is_list': True,
                          'required': True},
                         {'name': "auto_pass",
                          'is_list': False,
                          'required': False},
                         {'name': "unique",
                          'is_list': False,
                          'required': False},
                         {'name': "genopts",
                          'is_list': False,
                          'required': False}]
        item_list, auto_pass, unique, genopts = self._check_payload(
            payload_dicts)

        if auto_pass is True:
            # Retrieve words dictionary
            words = self._get_words(genopts)

            # Generate common password for all items
            if unique is not True:
                common_password = self._gen_pwd(words, genopts)

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            if auto_pass is True:
                if unique is True:
                    password = self._gen_pwd(words, genopts)
                else:
                    password = common_password
            else:
                password = None

            items.append(self.make_item(row, cipher, password))

        try:
            items = api.item_create(self.session, items)
            response = []
            for item in items:
                response.append(item.extract(cipher))
            return {'result': 'success', 'items': response}
        except Exception:
            raise bh.OppError("Unable to add new items to the database!")

    def _do_post(self, phrase):
        """
        Update a list of items. Similar options to create except that
        item id is required for each item in the list.

        :param phrase: decryption passphrase

        :returns: success result
        """
        payload_dicts = [{'name': "items",
                          'is_list': True,
                          'required': True},
                         {'name': "auto_pass",
                          'is_list': False,
                          'required': False},
                         {'name': "unique",
                          'is_list': False,
                          'required': False},
                         {'name': "genopts",
                          'is_list': False,
                          'required': False}]
        item_list, auto_pass, unique, genopts = self._check_payload(
            payload_dicts)

        if auto_pass is True:
            # Retrieve words dictionary
            words = self._get_words(genopts)

            # Generate common password for all items if needed
            if unique is not True:
                common_password = self._gen_pwd(words, genopts)

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            # Make sure item id is parsed from request
            try:
                item_id = row['id']
            except KeyError:
                raise bh.OppError("Missing item id in list!")
            if not item_id:
                raise bh.OppError("Empty item id in list!")

            if auto_pass is True:
                if unique is True:
                    password = self._gen_pwd(words, genopts)
                else:
                    password = common_password
            else:
                password = None

            items.append(self.make_item(row, cipher, password, item_id))

        try:
            api.item_update(self.session, items)
            response = []
            for item in items:
                response.append(item.extract(cipher))
            return {'result': 'success', 'items': response}
        except Exception:
            raise bh.OppError("Unable to update items in the database!")

    def _do_delete(self):
        """
        Delete a list of items, identified by id.

        :returns: success result
        """
        payload_dicts = [{'name': "ids",
                          'is_list': True,
                          'required': True}]
        payload_objects = self._check_payload(payload_dicts)
        id_list = payload_objects[0]

        try:
            api.item_delete_by_id(self.session, self.user, id_list)
            return {'result': "success"}
        except Exception:
            raise bh.OppError("Unable to delete items from the database!")
