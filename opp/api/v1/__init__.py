import base64
import bcrypt
import hashlib
import json
import logging

from flask import Flask, request

import categories
import items
import users
from opp.api.flask_jwt import JWT, jwt_required
from opp.db import api


# Logging config
logging.basicConfig(filename='/tmp/sinovox.log', level=logging.DEBUG)


# Flask app
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = "super-secret"
app.config['JWT_AUTH_URL_RULE'] = "/login"


if __name__ == "__main__":
    app.run()


def authenticate(username, password):
    user = api.user_get_by_username(username)
    if user:
        digest = base64.b64encode(hashlib.sha256(password).digest())
        if bcrypt.checkpw(digest, user.password.encode()):
            return user
    return None


def identity(payload):
    return api.user_get_by_id(payload['identity'])


jwt = JWT(app, authenticate, identity)


def _to_json(dictionary):
    return json.dumps(dictionary)


def _enforce_content_type():
    try:
        content_type = request.headers['Content-Type']
    except KeyError:
        return '{"error": "Mising Content-Type"}'
    if content_type != "application/json":
        return '{"error": "Invalid Content-Type"}'


@app.route("/api/v1/health")
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/users", methods=['PUT', 'POST', 'DELETE'])
def handle_users():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = users.ResponseHandler(request)
    response = handler.respond(require_phrase=False)
    return _to_json(response)


@app.route("/api/v1/categories",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_categories():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = categories.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)


@app.route("/api/v1/items",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_items():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = items.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)
