#!/usr/local/bin/python


import base_handler
from opp.common import aescipher, utils


class ResponseHandler(base_handler.BaseResponseHandler):

    def _handle_getall(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        self.db_cursor.execute("SELECT * from categories ORDER by id")
        categories = self.db_cursor.fetchall()
        for cat_id, category_blob in categories:
            cat = cipher.decrypt(category_blob)
            response.append({'id': cat_id, 'category': cat})

        return {'result': 'success', 'categories': response}

    def _handle_create(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        for cat in cat_list:
            if not cat:
                resp = {'category': None,
                        'status': "empty category not allowed"}
            else:
                # Encrypt category name blob
                cat_blob = cipher.encrypt(cat)

                # Store category name blob
                sql = ("INSERT INTO categories (category_blob)"
                       "VALUES (%s)" % utils.qq(cat_blob))
                if self.db_cursor.execute(sql) == 1:
                    resp = {'category': cat, 'status': "success: created"}
                else:
                    resp = {'category': cat,
                            'status': "error: failed to create"}

            payload.append(resp)

        return {'result': 'success', 'payload': payload}

    def _handle_update(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        payload = []
        cipher = aescipher.AESCipher(phrase)
        for cat in cat_list:
            if not cat:
                # Silently ignore any empty dictionaries
                continue
            try:
                # Make sure category id is parsed from request
                cat_id = cat['id']
            except KeyError:
                cat_id = None

            if not cat_id:
                cat['status'] = "error: missing or empty category id"
            else:
                try:
                    # Make sure category is parsed from request
                    category = cat['category']
                except KeyError:
                    category = None

                if not category:
                    cat['status'] = "error: missing or empty category"
                else:
                    cat_blob = utils.qq(cipher.encrypt(category))
                    sql = ("UPDATE categories SET category_blob = %s"
                           "WHERE id=%s" % (cat_blob, cat_id))
                if self.db_cursor.execute(sql) == 1:
                    cat['status'] = "success: updated"
                else:
                    cat['status'] = "error: does not exist"

            payload.append(cat)

        return {'result': 'success', 'payload': payload}

    def _handle_delete(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        payload = []
        for cat_id, cascade in cat_list:
            if not cat_id:
                resp = {'id': None, 'status': "error: empty category id"}
            else:
                sql = "DELETE FROM categories WHERE id=%s" % cat_id
                if self.db_cursor.execute(sql) == 1:
                    resp = {'id': cat_id, 'status': "success: deleted"}
                else:
                    resp = {'id': cat_id, 'status': "error: does not exist"}

                # TODO(alex_bash): report # entries removed to user?
                if cascade is True:
                    sql = "DELETE FROM entries WHERE category_id=%s" % cat_id
                else:
                    sql = ("UPDATE entries set category_id=NULL"
                           "WHERE category_id=%s" % cat_id)
                self.db_cursor.execute(sql)

            payload.append(resp)

        return {'result': 'success', 'payload': payload}
