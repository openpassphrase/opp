#!/usr/local/bin/python


from urlparse import parse_qs
import uuid
import wsgiref.util as wsgiutil


def extract_path(env):
    path = []
    while True:
        item = wsgiutil.shift_path_info(env)
        if not item:
            break
        path.append(item.lower())
    return path


def extract_query(env):
    try:
        qs = parse_qs(env['QUERY_STRING'])
    except ValueError:
        qs = None
    return qs


def qq(arg):
    return "'" + arg + "'"


def genuuid():
    return str(uuid.uuid4())
