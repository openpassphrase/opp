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
import logging
import shlex
import subprocess
import sys

from opp.common import opp_config


def execute(cmd, propagate=True):
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
        if propagate:
            raise RuntimeError(msg)
    return exitcode, out, err


def checkpw(password, hashed):
    digest = hashlib.sha256(password.encode()).digest()
    return bcrypt.checkpw(base64.b64encode(digest), hashed.encode())


def hashpw(password):
    digest = hashlib.sha256(password.encode()).digest()
    encoded = base64.b64encode(digest)
    return bcrypt.hashpw(encoded, bcrypt.gensalt())


def getLogger(name, config=None):
    config = config or opp_config.OppConfig()
    log_level = config['log_level'] or logging.DEBUG
    log_name = config['log_filename'] or '/tmp/openpassphrase.log'
    logger = logging.getLogger(name)

    if not logging.root.handlers:
        formatter = logging.Formatter(
            '%(levelname)-7s %(name)s %(asctime)s %(message)s')
        handler = logging.FileHandler(log_name)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    return logger
