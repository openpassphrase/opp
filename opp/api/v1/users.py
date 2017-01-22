import base64
import bcrypt
import hashlib

import base_handler
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
            digest = base64.b64encode(hashlib.sha256(password).digest())
            hashed = bcrypt.hashpw(digest, bcrypt.gensalt())
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
            digest = base64.b64encode(hashlib.sha256(old_password).digest())
            if not bcrypt.checkpw(digest, user.password.encode()):
                return self.error("Invalid password!")
            digest = base64.b64encode(hashlib.sha256(new_password).digest())
            user.password = bcrypt.hashpw(digest, bcrypt.gensalt())
            api.user_update(user, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update user in the database!")

    def _do_delete(self, phrase):
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
            digest = base64.b64encode(hashlib.sha256(password).digest())
            if not bcrypt.checkpw(digest, user.password.encode()):
                return self.error("Invalid password!")
            api.user_delete_by_username(username, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete user from the database!")
