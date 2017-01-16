import base_handler
from opp.common import aescipher
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _handle_getall(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        entries = api.entry_getall(session=self.session)
        for entry in entries:
            response.append(entry.decrypt(cipher))
        return {'result': 'success', 'entries': response}

    def _handle_create(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        entries = []
        for item in entry_list:
            # Make sure entry is parsed from request
            try:
                entry = item['entry']
            except KeyError:
                entry = None
            if not entry:
                item['status'] = "error: missing or empty entry"
                payload.append(item)
                continue

            # Parse category id from request
            try:
                cat_id = item['category_id']
                if not cat_id:
                    cat_id = None
            except KeyError:
                cat_id = None

            blob = cipher.encrypt(entry)
            entries.append(models.Entry(blob=blob, category_id=cat_id))
            item['status'] = "success: created"
            payload.append(item)

        api.entry_create_update(entries, session=self.session)

        return {'result': 'success', 'payload': payload}

    def _handle_update(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        entries = []
        for ent in entry_list:
            # Make sure entry id is parsed from request
            try:
                ent_id = ent['id']
            except KeyError:
                ent_id = None
            if not ent_id:
                ent['status'] = "error: missing or empty entry id"
                payload.append(ent)
                continue

            # Make sure entry is parsed from request
            try:
                entry = ent['entry']
            except KeyError:
                entry = None
            if not entry:
                ent['status'] = "error: missing or empty entry"
                payload.append(ent)
                continue

            # Make sure category id is parsed from request
            try:
                cat_id = ent['category_id']
            except KeyError:
                cat_id = None
            if not cat_id:
                ent['status'] = "error: missing or empty entry"
                payload.append(ent)
                continue

            blob = cipher.encrypt(entry)
            entries.append(models.Entry(id=ent_id, blob=blob,
                                        category_id=cat_id))
            ent['status'] = "success: updated"
            payload.append(ent)

        api.entry_create_update(entries, session=self.session)

        return {'result': 'success', 'payload': payload}

    def _handle_delete(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        payload = []
        entries = []
        for ent_id in entry_list:
            # Make sure entry id is parsed from request
            if not ent_id:
                resp = {'id': None,
                        'status': "error: empty entry id not allowed"}
            else:
                entries.append(ent_id)
                resp = {'id': ent_id, 'status': "success: deleted"}

            payload.append(resp)

        api.entry_delete_by_id(entries, session=self.session)

        return {'result': 'success', 'payload': payload}
