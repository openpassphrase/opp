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

        return {'result': "success", 'categories': response}

    def _do_put(self, phrase):
        cat_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Check for empty category value
            if not cat:
                return self.error("Empty category data in list!")
            try:
                blob = cipher.encrypt(cat)
                categories.append(models.Category(blob=blob))
            except TypeError:
                return self.error("Invalid category data in list!")

        try:
            api.category_create(categories, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new categories to the database!")

    def _do_post(self, phrase):
        cat_list, error = self._check_payload(expect_list=True)
        if error:
            return error

        cipher = aescipher.AESCipher(phrase)
        categories = []
        for cat in cat_list:
            # Make sure category id is parsed from request
            try:
                cat_id = cat['id']
            except KeyError:
                return self.error("Missing category id in list!")
            if not cat_id:
                return self.error("Empty category id in list!")

            # Make sure category is parsed from request
            try:
                category = cat['category']
            except KeyError:
                return self.error("Missing category in list!")
            if not category:
                return self.error("Empty category in list!")

            try:
                blob = cipher.encrypt(category)
                categories.append(models.Category(id=cat_id, blob=blob))
            except TypeError:
                return self.error("Invalid category data in list!")

        try:
            api.category_update(categories, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update categories in the database!")

    def _do_delete(self, phrase):
        payload, error = self._check_payload(expect_list=False)
        if error:
            return error

        try:
            cascade = payload['cascade']
        except KeyError:
            return self.error("Missing cascade value!")
        if cascade is not True and cascade is not False:
            return self.error("Invalid cascade value!")

        try:
            categories = payload['ids']
        except KeyError:
            return self.error("Missing category id list!")
        if not categories:
            return self.error("Empty category id list!")
        if not isinstance(categories, list):
            return self.error("Invalid category id list!")

        try:
            api.category_delete_by_id(categories,
                                      cascade, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete categories from the database!")
