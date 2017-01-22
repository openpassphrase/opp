import base64
import bcrypt
import hashlib

import base_handler
from opp.db import api, models


class ResponseHandler(base_handler.BaseResponseHandler):

    def _do_put(self, phrase):
        # Extract required username field
        try:
            username = self.request.form['username']
        except KeyError:
            return error("Missing username!")
        if username is None:
            return error("Empty username!")

        # Extract required password field
        try:
            password = self.request.form['password']
        except KeyError:
            return error("Missing password!")
        if password is None:
            return error("Empty password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if user:
                return error("User already exists!")
            digest = base64.b64encode(hashlib.sha256(password).digest())
            hashed = bcrypt.hashpw(digest, bcrypt.gensalt())
            user = models.User(username=username, password=hashed)
            api.user_create(user, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to add new user the database!")

    def _do_post(self, phrase):
        # Extract required username field
        try:
            username = self.request.form['username']
        except KeyError:
            return error("Missing username!")
        if username is None:
            return error("Empty username!")

        # Extract required old password field
        try:
            old_password = self.request.form['old_password']
        except KeyError:
            return error("Missing old_password!")
        if old_password is None:
            return error("Empty old_password!")

        # Extract required new password field
        try:
            new_password = self.request.form['new_password']
        except KeyError:
            return error("Missing new_password!")
        if new_password is None:
            return error("Empty new_password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if not user:
                return error("User doesn't exist!")
            digest = base64.b64encode(hashlib.sha256(old_password).digest())
            if not bcrypt.checkpw(digest, user.password.encode()):
                return error("Invalid password!")
            digest = base64.b64encode(hashlib.sha256(new_password).digest())
            user.password = bcrypt.hashpw(digest, bcrypt.gensalt())
            api.user_update(user, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to update user in the database!")

    def _do_delete(self, phrase):
        # Extract required username field
        try:
            username = self.request.form['username']
        except KeyError:
            return error("Missing username!")
        if username is None:
            return error("Empty username!")

        # Extract required password field
        try:
            password = self.request.form['password']
        except KeyError:
            return error("Missing password!")
        if password is None:
            return error("Empty password!")

        try:
            user = api.user_get_by_username(username, session=self.session)
            if not user:
                return error("User doesn't exist!")
            digest = base64.b64encode(hashlib.sha256(password).digest())
            if not bcrypt.checkpw(digest, user.password.encode()):
                return error("Invalid password!")
            api.user_delete_by_username(username, session=self.session)
            return {'result': "success"}
        except Exception:
            return self.error("Unable to delete user from the database!")
