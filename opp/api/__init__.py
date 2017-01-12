import json
import logging

from flask import Flask, request

import base_handler
import categories
from opp.common import utils
import entries


# Logging config
logging.basicConfig(filename='/tmp/sinovox.log', level=logging.DEBUG)


# Flask app
app = Flask(__name__)


if __name__ == "__main__":
    app.run()


def _to_json(dictionary):
    return json.dumps(dictionary)


@app.route("/")
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/categories", methods=['POST'])
def handle_categories():
    handler = categories.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)


@app.route("/entries", methods=['POST'])
def handle_entries():
    handler = entries.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)
