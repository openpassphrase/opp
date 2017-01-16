import json
import logging

from flask import Flask, request

import categories
import entries


# Logging config
logging.basicConfig(filename='/tmp/sinovox.log', level=logging.DEBUG)


# Flask app
app = Flask(__name__)


if __name__ == "__main__":
    app.run()


def _to_json(dictionary):
    return json.dumps(dictionary)


@app.route("/api/v1/health")
def health_check():
    return _to_json({'status': "OpenPassPhrase service is running"})


@app.route("/api/v1/categories", methods=['POST'])
def handle_categories():
    handler = categories.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)


@app.route("/api/v1/entries", methods=['POST'])
def handle_entries():
    handler = entries.ResponseHandler(request)
    response = handler.respond()
    return _to_json(response)
