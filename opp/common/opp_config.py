from config import Config, ConfigList, ConfigError
from os import path


class OppConfig(object):

    def __init__(self, top_config):
        usr_config = '~/.opp/opp.cfg'
        sys_config = '/etc/opp/opp.cfg'

        self.cfglist = ConfigList()

        # Load configs in order of decreasing priority
        if path.isfile(top_config):
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
