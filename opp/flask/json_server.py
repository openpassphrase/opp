# Copyright 2017 OpenPassPhrase
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import timedelta
import json


from flask import Flask, g, request, _app_ctx_stack
from flask_cors import CORS

from opp.api.v1 import base_handler, categories, fetch_all, items
from opp.common import opp_config, utils
from opp.db import api
from opp.flask.flask_jwt import JWT, jwt_required


CONF = opp_config.OppConfig()
LOG = utils.getLogger(__name__, CONF)


# JWT and session configs
CONF = opp_config.OppConfig()
if CONF['secret_key'] == "default-insecure":
    LOG.warning("Config option 'secret_key' not specified."
                " Using default insecure value!")
try:
    exp_delta = int(CONF['exp_delta'])
    if CONF['exp_delta'] > pow(2, 31):
        LOG.warning("Invalid value specified for 'exp_delta' "
                    "config option. Defaulting to 300 seconds.")
        exp_delta = 300
except Exception:
    LOG.warning("Invalid value specified for 'exp_delta' "
                "config option. Defaulting to 300 seconds.")
    exp_delta = 300

# Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = CONF['SECRET_KEY']
app.config['EXP_DELTA'] = timedelta(seconds=exp_delta)
app.config['PREFERRED_URL_SCHEME'] = "https"


@app.errorhandler(base_handler.OppError)
def error_handler(error):
    LOG.error(error)
    return error.json(), error.status, error.headers


@app.before_request
def get_scoped_session():
    g.session = api.get_scoped_session()


@app.teardown_appcontext
def shutdown_session(exception=None):
    if g.session:
        g.session.remove()


def authenticate(username, password):
    user = api.user_get_by_username(g.session, username)
    if user and utils.checkpw(password, user.password):
        return user


def identity(payload):
    return api.user_get_by_id(g.session, payload['identity'])


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
    user = _app_ctx_stack.top.current_identity
    handler = fetch_all.ResponseHandler(request, user, g.session)
    response = handler.respond()
    return _to_json(response)


@app.route("/v1/categories",
           methods=['GET', 'PUT', 'POST', 'DELETE'])
@jwt_required()
def handle_categories():
    err = _enforce_content_type()
    if err:
        return err, 400
    user = _app_ctx_stack.top.current_identity
    handler = categories.ResponseHandler(request, user, g.session)
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
    user = _app_ctx_stack.top.current_identity
    handler = items.ResponseHandler(request, user, g.session)
    # Set require_phrase to True for all methods except DELETE
    response = handler.respond(request.method != 'DELETE')
    return _to_json(response)
