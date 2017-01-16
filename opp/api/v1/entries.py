import base_handler
from opp.common import aescipher
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        entries = api.entry_getall(session=self.session)
        for entry in entries:
            response.append(entry.decrypt(cipher))

        return {'result': 'success', 'entries': response}

    def _do_put(self, phrase):
        entry_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        entries = []
        for item in entry_list:
            # Make sure entry is parsed from request
            try:
                entry = item['entry']
            except KeyError:
                return self.error("Missing entry data in list!")
            if not entry:
                return self.error("Empty entry data in list!")

            # Parse category id from request or set to None
            try:
                cat_id = item['category_id']
                if not cat_id:
                    cat_id = None
            except KeyError:
                cat_id = None

            try:
                blob = cipher.encrypt(entry)
                entries.append(models.Entry(blob=blob, category_id=cat_id))
            except TypeError:
                return self.error("Invalid entry data in list!")

        try:
            api.entry_create(entries, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new entries to the database!")

    def _do_post(self, phrase):
        entry_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        entries = []
        for ent in entry_list:
            # Make sure entry id is parsed from request
            try:
                ent_id = ent['id']
            except KeyError:
                return self.error("Missing entry id in list!")
            if not ent_id:
                return self.error("Empty entry id in list!")

            # Make sure entry is parsed from request
            try:
                entry = ent['entry']
            except KeyError:
                return self.error("Missing entry in list!")
            if not entry:
                return self.error("Empty entry in list!")

            # Make sure category id is parsed from request or set to None
            try:
                cat_id = ent['category_id']
            except KeyError:
                cat_id = None

            try:
                blob = cipher.encrypt(entry)
                entries.append(models.Entry(id=ent_id, blob=blob,
                                            category_id=cat_id))
            except TypeError:
                return self.error("Invalid entry data in list!")

        try:
            api.entry_update(entries, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update entries in the database!")

    def _do_delete(self, phrase):
        payload, error = self._check_payload(expect_list=True)
        if error:
            return error

        try:
            api.entry_delete_by_id(payload, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete entries from the database!")
