import bcrypt
import json
import logging

from flask import Flask, request
from flask_jwt import JWT, jwt_required

import categories
import items
import users
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
    if user and bcrypt.checkpw(password, user.password):
        return user
    return None


def identity(payload):
    return api.user_get_by_id(payload['identity'])


def _to_json(dictionary):
    return json.dumps(dictionary)


jwt = JWT(app, authenticate, identity)


@app.route("/api/v1/health")
#@jwt_required()
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/users", methods=['PUT', 'POST', 'DELETE'])
def handle_users():
    handler = users.ResponseHandler(request)
    response = handler.respond(require_phrase=False)
    return _to_json(response)


@app.route("/api/v1/categories",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
def handle_categories():
    handler = categories.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)


@app.route("/api/v1/items",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
def handle_items():
    handler = items.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)
