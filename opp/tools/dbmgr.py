#!/usr/bin/env python

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

import sys
from pickle import dump, load

import click
from sqlalchemy import create_engine, exc
from sqlalchemy_utils import database_exists, create_database

from opp.common import aescipher, opp_config, utils
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
              help="Enable verbose output")
@click.option('--config_file', default=None,
              help="User supplied configuration file")
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


@click.option('--phrase', default=None, required=True,
              help="passphrase for encryption")
@click.option('-p', default=None, required=True,
              help="password")
@click.option('-u', default=None, required=True,
              help="username")
@main.command(name='add-user')
@pass_config
def add_user(config, u, p, phrase):
    if len(phrase) < 6:
        sys.exit("Error: passphrase must be at least 6 characters long!")
    try:
        cipher = aescipher.AESCipher(phrase)
        ok = cipher.encrypt("OK")
        s = api.get_scoped_session(config.conf)
        with s.begin():
            user = api.user_get_by_username(s, u)
            if user:
                sys.exit("Error: user already exists!")
            hashed = utils.hashpw(p)
            user = models.User(username=u, password=hashed, phrase_check=ok)
            api.user_create(s, user)
            user = api.user_get_by_username(s, u)
            if user:
                print("Successfully added new user: %s" % u)
            else:
                print("Error: unable to add user: %s" % u)
    except Exception as e:
        sys.exit("Error: %s" % str(e))


@click.option('-p', default=None, required=True,
              help="password")
@click.option('-u', default=None, required=True,
              help="username")
@main.command(name='del-user')
@pass_config
def del_user(config, u, p):
    try:
        s = api.get_scoped_session(config.conf)
        with s.begin():
            user = api.user_get_by_username(s, u)
            if not user:
                sys.exit("Error: user does not exist!")
            if not utils.checkpw(p, user.password):
                sys.exit("Error: incorrect password!")
            api.user_delete(s, user)
            user = api.user_get_by_username(s, u)
            if user:
                print("Error: unable to delete user: %s" % u)
            else:
                print("Successfully deleted user: %s" % u)
    except Exception as e:
        sys.exit("Error: %s" % str(e))


@click.option('--new_phrase', default=None, required=True,
              help="New encryption passphrase")
@click.option('--old_phrase', default=None, required=True,
              help="Original passphrase for decryption")
@click.option('-p', default=None, required=True,
              help="password")
@click.option('-u', default=None, required=True,
              help="username")
@main.command(name='update-phrase')
@pass_config
def update_phrase(config, u, p, old_phrase, new_phrase):
    if len(new_phrase) < 6:
        sys.exit("Error: passphrase must be at least 6 characters long!")
    try:
        old_cipher = aescipher.AESCipher(old_phrase)
        new_cipher = aescipher.AESCipher(new_phrase)
        s = api.get_scoped_session(config.conf)
        with s.begin():
            user = api.user_get_by_username(s, u)
            if not user:
                sys.exit("Error: user does not exist!")
            if not utils.checkpw(p, user.password):
                sys.exit("Error: incorrect password!")
            try:
                if old_cipher.decrypt(user.phrase_check) != "OK":
                    sys.exit("Error: incorrect old passphrase supplied!")
            except UnicodeDecodeError:
                sys.exit("Error: incorrect old passphrase supplied!")

            printv(config, "Updating user information")
            user.phrase_check = new_cipher.encrypt("OK")
            api.user_update(s, user)
            printv(config, "Updating user's categories")
            categories = api.category_getall(s, user)
            for category in categories:
                category.recrypt(old_cipher, new_cipher)
            api.category_update(s, categories)
            printv(config, "Updating user's items")
            items = api.item_getall(s, user)
            for item in items:
                item.recrypt(old_cipher, new_cipher)
            api.item_update(s, items)
            print("All of user's data has been successfuly "
                  "re-encrypted with the new passphrase.")
    except Exception as e:
        sys.exit("Error: %s" % str(e))


@main.command()
@pass_config
def backup(config):  # pragma: no cover
    session = api.get_scoped_session(config.conf)
    for table in models.Base.metadata.sorted_tables:
        with open("%s.pickle" % table, "wb") as f:
            query = session.query(table)
            for row in query.all():
                dump(row, f)

    files = ["%s.pickle" % x.name for x in models.Base.metadata.sorted_tables]
    code, out, err = utils.execute("tar zcf opp.db.tz %s" % " ".join(files),
                                   propagate=False)
    if code != 0:
        sys.exit("Error creating database archive file: %s" % err)
    code, out, err = utils.execute("rm %s" % " ".join(files),
                                   propagate=False)
    if code != 0:
        print("Unable to remove .pickle files: %s" % err)
    print("Created database backup file: opp.db.tz")


@main.command()
@pass_config
def restore(config):  # pragma: no cover
    db_connect = config.conf['db_connect']
    if not db_connect:
        sys.exit("Error: database connection string not "
                 "found in any of the configuration files")
    try:
        engine = create_engine(db_connect)
    except exc.NoSuchModuleError as e:
        sys.exit("Error: %s" % str(e))

    if database_exists(engine.url):
        sys.exit("Error: database already exists, will not overwrite!")

    try:
        create_database(engine.url)
    except exc.OperationalError as e:
        sys.exit("Error: %s" % str(e))
    models.Base.metadata.create_all(engine)

    conn = engine.connect()

    print("Restoring database from backup file: opp.db.tz")
    code, out, err = utils.execute("tar zxf opp.db.tz", propagate=False)
    if code != 0:
        sys.exit("Error extracting database archive file: %s" % err)

    for table in models.Base.metadata.sorted_tables:
        with open("%s.pickle" % table, "rb") as f:
            while True:
                try:
                    ins = table.insert().values(load(f))
                    conn.execute(ins)
                except EOFError:
                    break

    files = ["%s.pickle" % x.name for x in models.Base.metadata.sorted_tables]
    code, out, err = utils.execute("rm %s" % " ".join(files))
    if code != 0:
        print("Unable to remove .pickle files: %s" % err)


if __name__ == '__main__':
    main()
