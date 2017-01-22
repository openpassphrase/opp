#!/usr/bin/env python

import sys

import click
from sqlalchemy import create_engine, exc
from sqlalchemy_utils import database_exists, create_database

from opp.common import opp_config
from opp.db import models


class Config:

    def __init__(self):
        self.verbose = False
        self.conf = []


pass_config = click.make_pass_decorator(Config, ensure=True)


def printv(config, msg):
    if config.verbose:
        print(msg)


@click.group()
@click.option('--verbose', is_flag=True,
              help='Enable verbose output')
@click.option('--config_file', default=None,
              help='User supplied configuration file')
@pass_config
def main(config, config_file, verbose):
    config.verbose = verbose
    config.conf = opp_config.OppConfig(config_file)


@main.command()
@pass_config
def init(config):
    sql_connect = config.conf['sql_connect']
    if sql_connect:
        try:
            engine = create_engine(sql_connect)
        except exc.NoSuchModuleError as e:
            sys.exit("Error: %s" % str(e))
        try:
            if not database_exists(engine.url):
                printv(config, "Creating database: 'openpassphrase'")
                create_database(engine.url)
        except exc.OperationalError as e:
            sys.exit("Error: %s" % str(e))
        printv(config, "Creating tables based on models")
        models.Base.metadata.create_all(engine)
    else:
        sys.exit("Error: database connection string not "
                 "found in any of the configuration files")


if __name__ == '__main__':
    main()
