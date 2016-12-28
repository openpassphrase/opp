#!/usr/local/bin/python

import cgitb
import json
import logging
from os import environ

import base_handler
import categories
from common import utils
import entries


# Disable this in production
cgitb.enable()
# Logging config
logging.basicConfig(filename='/tmp/sinovox.log', level=logging.DEBUG)


method = environ['REQUEST_METHOD']
query = utils.extract_query(environ)

path = utils.extract_path(environ)
if not path:
    response = {'status': 'error', 'message': "Endpoint not found!"}
else:
    if path[0] == 'categories':
        handler = categories.ResponseHandler(method, path, query)
    elif path[0] == 'entries':
        handler = entries.ResponseHandler(method, path, query)
    else:
        handler = base_handler.ErrorResponseHandler(
            "Endpoint not found!")

    response = handler.respond()

# Required response header
print("Content-type: text/html\n\n")
print(json.dumps(response))
