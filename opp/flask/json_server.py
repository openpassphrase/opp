# Copyright 2017 OpenPassPhrase
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applic/able law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import timedelta
import json
import logging

from flask import Flask, request
from flask_cors import CORS

from opp.api.v1 import categories, fetch_all, items
from opp.common import opp_config, utils
from opp.db import api
from opp.flask.flask_jwt import JWT, jwt_required


CONF = opp_config.OppConfig()


# Logging config
logname = CONF['log_filename'] or '/tmp/openpassphrase.log'
logging.basicConfig(filename=logname, level=logging.DEBUG)


# JWT and session configs
CONF = opp_config.OppConfig()
if CONF['secret_key'] == "default-insecure":
    logging.warning("Config option 'secret_key' not specified."
                    " Using default insecure value!")
try:
    exp_delta = int(CONF['exp_delta'])
    if CONF['exp_delta'] > pow(2, 31):
        logging.warning("Invalid value specified for 'exp_delta' "
                        "config option. Defaulting to 300 seconds.")
        exp_delta = 300
except Exception:
    logging.warning("Invalid value specified for 'exp_delta' "
                    "config option. Defaulting to 300 seconds.")
    exp_delta = 300

# Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = CONF['SECRET_KEY']
app.config['EXP_DELTA'] = timedelta(seconds=exp_delta)
app.config['PREFERRED_URL_SCHEME'] = "https"


def authenticate(username, password):
    user = api.user_get_by_username(username)
    if user and utils.checkpw(password, user.password):
        return user
    return None


def identity(payload):
    return api.user_get_by_id(payload['identity'])


def _to_json(dictionary):
    return json.dumps(dictionary)


def _enforce_content_type():
    if request.method == 'GET':
        return
    try:
        content_type = request.headers['Content-Type']
    except KeyError:
        return '{"error": "Mising Content-Type"}'
    if content_type != "application/json":
        return '{"error": "Invalid Content-Type"}'


# JWT helper
jwt = JWT(app, authenticate, identity)


@app.route("/v1/health")
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/v1/fetchall")
@jwt_required()
def handle_fetchall():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = fetch_all.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)


@app.route("/v1/categories",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_categories():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = categories.ResponseHandler(request)
    # Set require_phrase to True for all methods except DELETE
    response = handler.respond(request.method != 'DELETE')
    return _to_json(response)


@app.route("/v1/items",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_items():
    err = _enforce_content_type()
    if err:
        return err, 400
    handler = items.ResponseHandler(request)
    # Set require_phrase to True for all methods except DELETE
    response = handler.respond(request.method != 'DELETE')
    return _to_json(response)
