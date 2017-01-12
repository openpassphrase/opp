import json

from opp.db import api


def error(msg=None):
    return {'result': 'error', 'message': msg}


class BaseResponseHandler(object):

    def __init__(self, request):
        self.request = request

    def _get_payload(self):
        try:
            payload = self.request.form['payload']
        except KeyError:
            return [], error("Payload missing!")
        try:
            decoded = json.loads(payload)
        except ValueError:
            return [], error("Invalid payload!")

        if not decoded:
            return [], error("Empty payload!")

        return decoded, None

    def _handle_getall(self, phrase):
        return error("Action not implemented")

    def _handle_create(self, phrase):
        return error("Action not implemented")

    def _handle_update(self, phrase):
        return error("Action not implemented")

    def _handle_delete(self, phrase):
        return error("Action not implemented")

    def respond(self):
        # Retrieve required 'phrase' and 'action' fields
        try:
            phrase = self.request.form['phrase']
        except KeyError:
            return error("Passphrase missing!")
        try:
            action = self.request.form['action']
        except KeyError:
            return error("Action missing!")

        # Obtain DB session for making transactions
        self.session = api.get_session()

        if action == 'getall':
            response = self._handle_getall(phrase)
        elif action == 'create':
            response = self._handle_create(phrase)
        elif action == 'update':
            response = self._handle_update(phrase)
        elif action == 'delete':
            response = self._handle_delete(phrase)
        else:
            response = error("Action unrecognized!")

        self.session.close()
        return response


class ErrorResponseHandler(object):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return error(self.message)
