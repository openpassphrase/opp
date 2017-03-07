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

from os import path as ospath

from flask import Flask, send_from_directory

from opp.common import opp_config

CONF = opp_config.OppConfig()
if CONF['static_folder']:
    STATIC_FOLDER = CONF['static_folder']
else:
    STATIC_FOLDER = "/".join([ospath.dirname(ospath.realpath(__file__)),
                             "static"])


# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = CONF['SECRET_KEY']
app.config['PREFERRED_URL_SCHEME'] = "https"


@app.route('/')
def index():
    return send_from_directory(STATIC_FOLDER, 'index.html')


@app.route('/<path:filename>')
def angular(filename):
    gzip = False
    full_path = "/".join([STATIC_FOLDER, filename])
    if not ospath.isfile(full_path):
        filename = "index.html"
    elif ospath.isfile(".".join([full_path, "gz"])):
        filename = ".".join([filename, "gz"])
        gzip = True
    response = send_from_directory(STATIC_FOLDER, filename)
    if gzip:
        response.headers['Content-Encoding'] = 'gzip'
    return response
