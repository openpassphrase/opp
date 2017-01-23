import json
import logging

from flask import Flask, request

import categories
import items
import users
from opp.api.flask_jwt import JWT, jwt_required
from opp.common import opp_config, utils
from opp.db import api


CONF = opp_config.OppConfig()

# Logging config
logname = CONF['log_filename'] or '/tmp/openpassphrase.log'
logging.basicConfig(filename=logname, level=logging.DEBUG)


# Flask app
secretkey = CONF['jwt_secret_key']
if not secretkey:
    msg = ("Config option 'jwt_secret_key' not specified. "
           "Using default insecure value!")
    logging.warning(msg)
    secretkey = 'default-insecure'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = secretkey


if __name__ == "__main__":
    app.run()


def authenticate(username, password):
    user = api.user_get_by_username(username)
    if user and utils.checkpw(password, user.password):
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
