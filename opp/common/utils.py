import base64
import bcrypt
import hashlib
import shlex
import subprocess
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


def execute(cmd):
    args = shlex.split(cmd)
    process = subprocess.Popen(args,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    result = process.communicate()
    (out, err) = result
    exitcode = process.returncode

    if exitcode != 0:
        msg = ("Command %(cmd)s did not succeed. Returned an exit "
               "code of %(exitcode)d."
               "\n\nSTDOUT: %(out)s"
               "\n\nSTDERR: %(err)s" % {'cmd': cmd, 'exitcode': exitcode,
                                        'out': out, 'err': err})
        raise RuntimeError(msg)
    return exitcode, out, err


def checkpw(password, hashed):
    digest = hashlib.sha256(password).digest()
    encoded = base64.b64encode(digest)
    return bcrypt.checkpw(encoded, hashed.encode())


def hashpw(password):
    digest = hashlib.sha256(password).digest()
    encoded = base64.b64encode(digest)
    return bcrypt.hashpw(encoded, bcrypt.gensalt())

