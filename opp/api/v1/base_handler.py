import json

from opp.db import api


class BaseResponseHandler(object):

    def __init__(self, request):
        self.request = request

    def error(self, msg=None):
        return {'result': "error", 'message': msg}

    def _check_payload(self, expect_list):
        try:
            payload = self.request.form['payload']
        except KeyError:
            return None, self.error("Payload missing!")

        if not payload:
            return None, self.error("Empty payload!")

        try:
            decoded = json.loads(payload)
        except ValueError:
            return None, self.error("Invalid payload!")

        if expect_list:
            if not isinstance(decoded, list):
                return None, self.error("Payload should be in list form!")
        else:
            if isinstance(decoded, list):
                return None, self.error("Payload should not be in list form!")

        return decoded, None

    def _do_get(self, phrase):
        return self.error("Action not implemented")

    def _do_put(self, phrase):
        return self.error("Action not implemented")

    def _do_post(self, phrase):
        return self.error("Action not implemented")

    def _do_delete(self, phrase):
        return self.error("Action not implemented")

    def respond(self, require_phrase=True):
        if require_phrase:
            try:
                phrase = self.request.headers['x-opp-phrase']
            except KeyError:
                return self.error("Passphrase header missing!")
        else:
            phrase = None

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
            response = self.error("Method not supported!")

        self.session.close()
        return response


class ErrorResponseHandler(BaseResponseHandler):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return self.error(self.message)
