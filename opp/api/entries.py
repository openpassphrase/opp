#!/usr/local/bin/python


import base_handler
from opp.common import aescipher, utils


class ResponseHandler(base_handler.BaseResponseHandler):

    def _handle_getall(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        sql = ("SELECT e.id, e.entry_blob, e.category_id, "
               "c.category_blob FROM entries AS e LEFT JOIN "
               "(categories AS c) ON (e.category_id=c.id) "
               " ORDER BY e.id")
        self.db_cursor.execute(sql)
        entries = self.db_cursor.fetchall()
        for item in entries:
            resp = {'id': item[0],
                    'entry': cipher.decrypt(item[1]),
                    'category_id': item[2]}
            try:
                resp['category'] = cipher.decrypt(item[3])
            except TypeError:
                resp['category'] = None

            response.append(resp)
        return {'result': 'success', 'entries': response}

    def _handle_create(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        for item in entry_list:
            if not item:
                # Silently ignore any empty dictionaries
                continue
            try:
                # Make sure category id is parsed from request
                cat_id = item['category_id']
                if not cat_id:
                    cat_id = "NULL"
            except KeyError:
                cat_id = "NULL"

            try:
                # Make sure entry is parsed from request
                entry = item['entry']
            except KeyError:
                entry = None
            if not entry:
                item['status'] = "error: missing or empty entry"
            else:
                # Encrypt entry blob
                ent_blob = cipher.encrypt(entry)

                # Store entry
                sql = ("INSERT INTO entries (category_id,"
                       "entry_blob) VALUES (%s,%s)" %
                       (cat_id, utils.qq(ent_blob)))
                if self.db_cursor.execute(sql) == 1:
                    item['status'] = "success: created"
                else:
                    item['status'] = "error: failed to create"

            payload.append(item)

        return {'result': 'success', 'payload': payload}

    def _handle_update(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        payload = []
        cipher = aescipher.AESCipher(phrase)
        for ent in entry_list:
            if not ent:
                # Silently ignore any empty dictionaries
                continue
            try:
                # Make sure entry id is parsed from request
                ent_id = ent['id']
            except KeyError:
                ent_id = None

            if not ent_id:
                ent['status'] = "error: missing or empty entry id"
            else:
                try:
                    # Make sure entry is parsed from request
                    entry = ent['entry']
                except KeyError:
                    entry = None
                if not entry:
                    ent['status'] = "error: missing or empty entry"
                else:
                    entry_blob = utils.qq(cipher.encrypt(entry))
                    try:
                        cat_id = ent['category_id']
                        if not cat_id:
                            cat_id = "NULL"
                    except KeyError:
                        cat_id = "NULL"
                    sql = ("UPDATE entries SET "
                           "entry_blob = %s, "
                           "category_id = %s "
                           "WHERE id=%s" % (entry_blob,
                                            cat_id,
                                            ent_id))
                    if self.db_cursor.execute(sql) == 1:
                        ent['status'] = "success: updated"
                    else:
                        ent['status'] = "error: does not exist"

            payload.append(ent)

        return {'result': 'success', 'payload': payload}

    def _handle_delete(self, phrase):
        entry_list, error = self._get_payload()
        if error:
            return error

        payload = []
        for ent_id in entry_list:
            if not ent_id:
                resp = {'id': None,
                        'status': "error: empty entry id not allowed"}
            else:
                sql = "DELETE FROM entries WHERE id=%s" % ent_id
                if self.db_cursor.execute(sql) == 1:
                    resp = {'id': ent_id, 'status': "success: deleted"}
                else:
                    resp = {'id': ent_id, 'status': "error: does not exist"}

            payload.append(resp)

        return {'result': 'success', 'payload': payload}
