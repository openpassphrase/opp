from datetime import timedelta
import json
import logging

from flask import Flask, request

from opp.api.v1 import categories, items, users
from opp.common import opp_config, utils
from opp.db import api
from opp.flask.flask_jwt import JWT, jwt_required


CONF = opp_config.OppConfig()

# Logging config
logname = CONF['log_filename'] or '/tmp/openpassphrase.log'
logging.basicConfig(filename=logname, level=logging.DEBUG)


# JWT configs
jwt_secret_key = CONF['jwt_secret_key']
if not jwt_secret_key:
    msg = ("Config option 'jwt_secret_key' not specified. "
           "Using default insecure value!")
    logging.warning(msg)
    jwt_secret_key = 'default-insecure'
try:
    jwt_exp_delta = int(CONF['jwt_exp_delta']) or 300
    if not jwt_exp_delta or jwt_exp_delta > pow(2, 31):
        msg = ("Invalid value specified for 'jwt_exp_delta' config option. "
               "Defaulting to 300 seconds.")
        logging.warning(msg)
        jwt_exp_delta = 300
except Exception:
    msg = ("Invalid value specified for 'jwt_exp_delta' config option. "
           "Defaulting to 300 seconds.")
    logging.warning(msg)
    jwt_exp_delta = 300

# Flask app
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_EXP_DELTA'] = timedelta(seconds=jwt_exp_delta)
app.config['PREFERRED_URL_SCHEME'] = "https"

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
