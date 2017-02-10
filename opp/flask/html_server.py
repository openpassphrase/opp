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

import logging

from flask import Flask, redirect, request, session, url_for
from flask import send_from_directory

from opp.common import opp_config, utils
from opp.db import api


CONF = opp_config.OppConfig()


# Logging config
logname = CONF['log_filename'] or '/tmp/openpassphrase.log'
logging.basicConfig(filename=logname, level=logging.DEBUG)


# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = CONF['SECRET_KEY']
app.config['PREFERRED_URL_SCHEME'] = "https"


def authenticate(username, password):
    user = api.user_get_by_username(username)
    if user and utils.checkpw(password, user.password):
        return user
    return None


@app.route('/opp')
def index():
    return app.send_static_file('index.html')

@app.route('/opp/<path:filename>')
def angular(filename):
    return send_from_directory('static', filename)

