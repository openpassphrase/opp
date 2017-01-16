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
        except (ValueError, TypeError):
            return [], error("Invalid payload!")

        if not decoded:
            return [], error("Empty payload!")

        return decoded, None

    def _do_get(self, phrase):
        return error("Action not implemented")

    def _do_put(self, phrase):
        return error("Action not implemented")

    def _do_post(self, phrase):
        return error("Action not implemented")

    def _do_delete(self, phrase):
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
            response = self._do_get(phrase)
        elif self.request.method == 'PUT':
            response = self._do_put(phrase)
        elif self.request.method == 'POST':
            response = self._do_post(phrase)
        elif self.request.method == 'DELETE':
            response = self._do_delete(phrase)
        else:
            response = error("Method not supported!")

        self.session.close()
        return response


class ErrorResponseHandler(object):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return error(self.message)
