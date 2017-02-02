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

from sqlalchemy import create_engine, event, exc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, subqueryload

from opp.common import opp_config
from opp.db import models


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_scoped_session(conf=None):
    conf = conf or opp_config.OppConfig(conf)
    if conf['db_connect']:
        try:
            engine = create_engine(conf['db_connect'])
            session_factory = sessionmaker(engine, autocommit=True)
            return scoped_session(session_factory)
        except exc.NoSuchModuleError as e:
            sys.exit("Error: %s" % str(e))
        sys.exit("Error: database connection string not configured.")


def user_create(session, user):
    if session and user:
        session.add(user)


def user_update(session, user):
    if session and user:
        session.merge(user)


def user_get_by_id(session, id):
    if session and id:
        query = session.query(models.User).filter(
            models.User.id == id)
        return query.one_or_none()
    return None


def user_get_by_username(session, username):
    if session and username:
        query = session.query(models.User).filter(
            models.User.username == username)
        return query.one_or_none()
    return None


def user_delete(session, user):
    if session and user:
        session.delete(user)


def user_delete_by_username(session, username):
    user = user_get_by_username(session, username)
    user_delete(session, user)


def category_create(session, categories):
    if session and categories:
        session.add_all(categories)
        session.flush()
        return categories


def category_update(session, categories):
    if session:
        for category in categories:
            session.merge(category)


def category_getall(session, user, filter_ids=None):
    if session and user:
        session.add(user)
        if filter_ids:
            query = session.query(models.Category).order_by(
                models.Category.id).filter(
                models.Category.id.in_(filter_ids)).filter(
                models.User.id == user.id).options(
                subqueryload(models.Category.items))
        else:
            query = session.query(models.Category).filter(
                models.User.id == user.id).order_by(
                models.Category.id).options(
                subqueryload(models.Category.items))
        return query.all()


def category_delete(session, categories, cascade):
    if session:
        if cascade:
            for category in categories:
                for item in category.items:
                    session.delete(item)
                session.delete(category)
        else:
            for category in categories:
                for item in category.items:
                    item.category_id = None
                    session.add(item)
                session.delete(category)


def category_delete_by_id(session, user, filter_ids, cascade):
    categories = category_getall(session, user, filter_ids)
    category_delete(session, categories, cascade)


def item_create(session, items):
    if session and items:
        session.add_all(items)
        session.flush()
        return items


def item_update(session, items):
    if session:
        for item in items:
            session.merge(item)


def item_getall(session, user, filter_ids=None):
    if session and user:
        session.add(user)
        if filter_ids:
            query = session.query(
                models.Item).order_by(
                models.Item.id).filter(
                models.Item.id.in_(filter_ids)).filter(
                models.User.id == user.id).outerjoin(
                models.Category).options(
                subqueryload(models.Item.category))

        else:
            query = session.query(
                models.Item).order_by(
                models.Item.id).filter(
                models.User.id == user.id).outerjoin(
                models.Category).options(
                subqueryload(models.Item.category))
        return query.all()


def item_getall_orphan(session, user):
    if session and user:
        session.add(user)
        query = session.query(
            models.Item).order_by(
            models.Item.id).filter(
            models.User.id == user.id).filter(
            models.Item.category_id.is_(None))
        return query.all()


def item_delete(session, items):
    if session:
        for item in items:
            session.delete(item)


def item_delete_by_id(session, user, filter_ids):
    if filter_ids:
        items = item_getall(session, user, filter_ids)
        item_delete(session, items)
