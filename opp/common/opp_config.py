from config import Config, ConfigList, ConfigError
from os import environ, path


class OppConfig(object):

    def __init__(self, top_config=None):
        usr_config = path.expanduser('~/.opp/opp.cfg')
        sys_config = '/etc/opp/opp.cfg'

        self.cfglist = ConfigList()

        if not top_config:
            # User config not provided, attempt to read from env
            # This is mostly intended to be used for testing
            try:
                top_config = environ['OPP_TOP_CONFIG']
            except KeyError:
                pass

        # Load configs in order of decreasing priority
        if top_config and path.isfile(top_config):
            self.cfglist.append(Config(file(top_config)))
        if path.isfile(usr_config):
            self.cfglist.append(Config(file(usr_config)))
        if path.isfile(sys_config):
            self.cfglist.append(Config(file(sys_config)))

    def __getitem__(self, item):
        try:
            return self.cfglist.getByPath(item)
        except ConfigError:
            return None
