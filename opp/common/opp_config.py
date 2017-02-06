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

from six.moves import configparser
from os import environ, path
import sys


class OppConfig(object):

    def __init__(self, top_config=None):
        usr_config = path.expanduser('~/.opp/opp.cfg')
        sys_config = '/etc/opp/opp.cfg'

        if not top_config:
            # User config not provided, attempt to read from env
            # This is mostly intended to be used for testing
            try:
                top_config = environ['OPP_TOP_CONFIG']
            except KeyError:
                pass

        # Create config list in order of increasing priority
        cfglist = []
        if path.isfile(sys_config):
            cfglist.append(sys_config)
        if path.isfile(usr_config):
            cfglist.append(usr_config)
        if top_config and path.isfile(top_config):
            cfglist.append(top_config)

        if sys.version_info >= (3, 2):
            self.cfg = configparser.ConfigParser()
        else:
            self.cfg = configparser.SafeConfigParser()

        if cfglist:
            self.cfg.read(cfglist)

        # Set default values
        self.def_sec = "DEFAULT"
        cfg_defaults = [
            ['secret_key', "default-insecure"],
            ['exp_delta', "300"]]
        for opt in cfg_defaults:
            if not self.cfg.has_option(self.def_sec, opt[0]):
                self.cfg.set(self.def_sec, opt[0], opt[1])

    def __getitem__(self, item):
        try:
            return self.cfg.get(self.def_sec, item)
        except configparser.Error:
            return None
