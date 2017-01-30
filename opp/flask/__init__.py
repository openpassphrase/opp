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

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from opp.flask.html_server import app as html_app
from opp.flask.json_server import app as json_app


app = DispatcherMiddleware(html_app, {'/api': json_app})

if __name__ == '__main__':
    run_simple('192.168.1.15', 5000, app, use_evalex=True,
               use_reloader=True, use_debugger=True)
