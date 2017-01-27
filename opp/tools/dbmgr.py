#!/usr/bin/env python

import sys

import click
from sqlalchemy import create_engine, exc
from sqlalchemy_utils import database_exists, create_database

from opp.common import opp_config, utils
from opp.db import api, models


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
    db_connect = config.conf['db_connect']
    if not db_connect:
        sys.exit("Error: database connection string not "
                 "found in any of the configuration files")
    try:
        engine = create_engine(db_connect)
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


@click.option('-p', default=None, required=True,
              help='password')
@click.option('-u', default=None, required=True,
              help='username')
@main.command(name='add-user')
@pass_config
def add_user(config, u, p):
    try:
        user = api.user_get_by_username(u, conf=config.conf)
        if user:
            sys.exit("Error: user already exists!")
        hashed = utils.hashpw(p)
        user = models.User(username=u, password=hashed)
        api.user_create(user, conf=config.conf)
        user = api.user_get_by_username(u, conf=config.conf)
        if user:
            print("Successfully added new user: %s" % u)
        else:
            print("Error: unable to add user: %s" % u)
    except Exception as e:
        sys.exit("Error: %s" % str(e))


@click.option('-p', default=None, required=True,
              help='password')
@click.option('-u', default=None, required=True,
              help='username')
@main.command(name='del-user')
@pass_config
def del_user(config, u, p):
    try:
        session = api.get_session(config.conf)
        user = api.user_get_by_username(u, session=session)
        if not user:
            sys.exit("Error: user does not exist!")
        if not utils.checkpw(p, user.password):
            sys.exit("Error: incorrect password!")
        api.user_delete(user, session=session)
        user = api.user_get_by_username(u, session=session)
        if user:
            print("Error: unable to delete user: %s" % u)
        else:
            print("Successfully deleted user: %s" % u)
    except Exception as e:
        sys.exit("Error: %s" % str(e))


if __name__ == '__main__':
    main()
