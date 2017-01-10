import cgi
import json


def error(msg=None):
    return {'result': 'error', 'message': msg}


class BaseResponseHandler(object):

    def __init__(self, method, path, query):
        self.method = method
        self.path = path
        self.query = query
        self.form_data = cgi.FieldStorage()

    def _get_payload(self):
        try:
            payload = self.form_data['payload'].value
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
        # Only POST is supported at this point
        if self.method != 'POST':
            return error(("Method %s is not implemented!" % self.method))
        # Retrieve required 'phrase' and 'action' fields
        try:
            phrase = self.form_data['phrase'].value
        except KeyError:
            return error("Passphrase missing!")
        try:
            action = self.form_data['action'].value
        except KeyError:
            return error("Action missing!")

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

        return response


class ErrorResponseHandler(object):
    def __init__(self, message):
        self.message = message

    def respond(self):
        return error(self.message)
