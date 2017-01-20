import base_handler
from opp.common import aescipher
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_get(self, phrase):
        response = []
        cipher = aescipher.AESCipher(phrase)
        items = api.item_getall(session=self.session)
        for item in items:
            response.append(item.decrypt(cipher))

        return {'result': 'success', 'items': response}

    def _do_put(self, phrase):
        item_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            # Make sure item is parsed from request
            try:
                item = row['item']
            except KeyError:
                return self.error("Missing item data in list!")
            if not item:
                return self.error("Empty item data in list!")

            # Parse category id from request or set to None
            try:
                cat_id = row['category_id']
                if not cat_id:
                    cat_id = None
            except KeyError:
                cat_id = None

            try:
                blob = cipher.encrypt(item)
                items.append(models.Item(blob=blob, category_id=cat_id))
            except TypeError:
                return self.error("Invalid item data in list!")

        try:
            api.item_create(items, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new items to the database!")

    def _do_post(self, phrase):
        item_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        items = []
        for row in item_list:
            # Make sure item id is parsed from request
            try:
                item_id = row['id']
            except KeyError:
                return self.error("Missing item id in list!")
            if not item_id:
                return self.error("Empty item id in list!")

            # Make sure item is parsed from request
            try:
                item = row['item']
            except KeyError:
                return self.error("Missing item in list!")
            if not item:
                return self.error("Empty item in list!")

            # Make sure category id is parsed from request or set to None
            try:
                cat_id = row['category_id']
            except KeyError:
                cat_id = None

            try:
                blob = cipher.encrypt(item)
                items.append(models.Item(id=item_id, blob=blob,
                                         category_id=cat_id))
            except TypeError:
                return self.error("Invalid item data in list!")

        try:
            api.item_update(items, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update items in the database!")

    def _do_delete(self, phrase):
        payload, error = self._check_payload(expect_list=True)
        if error:
            return error

        try:
            api.item_delete_by_id(payload, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete items from the database!")
