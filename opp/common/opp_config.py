from six.moves import configparser
from os import environ, path


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
