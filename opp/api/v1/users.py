from opp.api.v1 import base_handler
from opp.common import utils
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_put(self, phrase):
        request_body = self.request.get_json()

        # Check required username field
        try:
            username = request_body['username']
        except KeyError:
            return self.error("Missing username!")
        if not username:
            return self.error("Empty username!")

        # Extract required password field
        try:
            password = request_body['password']
        except KeyError:
            return self.error("Missing password!")
        if not password:
            return self.error("Empty password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if user:
                return self.error("User already exists!")
            hashed = utils.hashpw(password)
            user = models.User(username=username, password=hashed)
            api.user_create(user, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new user the database!")

    def _do_post(self, phrase):
        request_body = self.request.get_json()

        # Extract required username field
        try:
            username = request_body['username']
        except KeyError:
            return self.error("Missing username!")
        if not username:
            return self.error("Empty username!")

        # Extract required old password field
        try:
            old_password = request_body['current_password']
        except KeyError:
            return self.error("Missing current password!")
        if not old_password:
            return self.error("Empty current password!")

        # Extract required new password field
        try:
            new_password = request_body['new_password']
        except KeyError:
            return self.error("Missing new password!")
        if not new_password:
            return self.error("Empty new password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if not user:
                return self.error("User doesn't exist!")
            if not utils.checkpw(old_password, user.password):
                return self.error("Invalid password!")
            user.password = utils.hashpw(new_password)
            api.user_update(user, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update user in the database!")

    def _do_delete(self):
        request_body = self.request.get_json()

        # Extract required username field
        try:
            username = request_body['username']
        except KeyError:
            return self.error("Missing username!")
        if not username:
            return self.error("Empty username!")

        # Extract required password field
        try:
            password = request_body['password']
        except KeyError:
            return self.error("Missing password!")
        if not password:
            return self.error("Empty password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if not user:
                return self.error("User doesn't exist!")
            if not utils.checkpw(password, user.password):
                return self.error("Invalid password!")
            api.user_delete_by_username(username, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete user from the database!")
