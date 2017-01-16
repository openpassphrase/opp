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
            phrase = self.request.headers['x-opp-phrase']
        except KeyError:
            return error("Passphrase header missing!")

        # Obtain DB session for making transactions
        self.session = api.get_session()

        if self.request.method == 'GET':
            response = self._handle_getall(phrase)
        elif self.request.method == 'PUT':
            response = self._handle_create(phrase)
        elif self.request.method == 'POST':
            response = self._handle_update(phrase)
        elif self.request.method == 'DELETE':
            response = self._handle_delete(phrase)
        else:
            response = error("Method not supported!")

        self.session.close()
        return response


class ErrorResponseHandler(object):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return error(self.message)
