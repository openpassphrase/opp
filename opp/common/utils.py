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

import base64
import bcrypt
import hashlib
import shlex
import subprocess
import sys


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
    digest = hashlib.sha256(password.encode()).digest()
    encoded = base64.b64encode(digest)
    if sys.version_info >= (3, 0):
        return bcrypt.checkpw(encoded, hashed)
    else:
        return bcrypt.checkpw(encoded, hashed.encode())


def hashpw(password):
    digest = hashlib.sha256(password.encode()).digest()
    encoded = base64.b64encode(digest)
    return bcrypt.hashpw(encoded, bcrypt.gensalt())
