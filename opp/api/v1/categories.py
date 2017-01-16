import base_handler
from opp.db import api, models
from opp.common import aescipher


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        categories = api.category_getall(session=self.session)
        for category in categories:
            response.append(category.decrypt(cipher))

        return {'result': 'success', 'categories': response}

    def _do_put(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        categories = []
        for cat in cat_list:
            if not cat:
                resp = {'category': None,
                        'status': "empty category not allowed"}
            else:
                # Encrypt category name blob and append to list
                blob = cipher.encrypt(cat)
                categories.append(models.Category(blob=blob))
                resp = {'category': cat, 'status': "success: created"}

            payload.append(resp)

        api.category_create(categories, session=self.session)

        return {'result': 'success', 'payload': payload}

    def _do_post(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        payload = []
        categories = []
        for cat in cat_list:
            # Make sure category id is parsed from request
            try:
                cat_id = cat['id']
            except KeyError:
                cat_id = None
            if not cat_id:
                cat['status'] = "error: missing or empty category id"
                payload.append(cat)
                continue

            # Make sure category is parsed from request
            try:
                category = cat['category']
            except KeyError:
                category = None
            if not category:
                cat['status'] = "error: missing or empty category"
                payload.append(cat)
                continue

            blob = cipher.encrypt(category)
            categories.append(models.Category(id=cat_id, blob=blob))
            cat['status'] = "success: updated"
            payload.append(cat)

        api.category_update(categories, session=self.session)

        return {'result': 'success', 'payload': payload}

    def _do_delete(self, phrase):
        cat_list, error = self._get_payload()
        if error:
            return error

        payload = []
        categories = []
        for category in cat_list:
            # Make sure category id is parsed from request
            try:
                cat_id = category['id']
            except KeyError:
                cat_id = None
            if not cat_id:
                resp = {'id': None, 'status': "error: missing category id"}
                payload.append(resp)
                continue

            # Make sure cascade value is parsed from request
            try:
                cascade = category['cascade']
            except KeyError:
                resp = {'id': None, 'status': "error: missing cascade value"}
                payload.append(resp)
                continue

            categories.append(cat_id)
            resp = {'id': cat_id, 'status': "success: deleted"}

            if cascade is True:
                pass
                # TODO(alex_bash): delete associated entries
            else:
                pass
                # TODO(alex_bash): clear category in associated entries

            payload.append(resp)

        api.category_delete_by_id(categories, session=self.session)

        return {'result': 'success', 'payload': payload}
