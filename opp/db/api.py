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
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker, subqueryload

from opp.common import opp_config
from opp.db import models


def get_session(conf=None):
    conf = conf or opp_config.OppConfig()
    db_connect = conf['db_connect']
    if db_connect:
        try:
            engine = create_engine(db_connect)
            session_factory = sessionmaker(engine, autocommit=True)
            Session = scoped_session(session_factory)
            return Session()
        except exc.NoSuchModuleError as e:
            sys.exit("Error: %s" % str(e))
    sys.exit("Error: database connection string not configured.")


def user_create(user, conf=None):
    if user:
        session = get_session(conf)
        with session.begin():
            session.add(user)


def user_update(user, conf=None):
    if user:
        session = get_session(conf)
        with session.begin():
            session.merge(user)


def user_get_by_id(id, conf=None):
    if id:
        session = get_session(conf)
        query = session.query(models.User).filter(
            models.User.id == id)
        return query.one_or_none()
    return None


def user_get_by_username(username, session=None, conf=None):
    if username:
        session = session or get_session(conf)
        query = session.query(models.User).filter(
            models.User.username == username)
        return query.one_or_none()
    return None


def user_delete(user, session=None, conf=None):
    if user:
        session = session or get_session(conf)
        with session.begin():
            session.delete(user)


def user_delete_by_username(username, conf=None):
    if username:
        session = get_session(conf)
        user = user_get_by_username(username, session, conf)
        user_delete(user, session, conf)


def category_create(categories, conf=None):
    if categories:
        session = get_session(conf)
        with session.begin():
            session.add_all(categories)


def category_update(categories, conf=None):
    session = get_session(conf)
    with session.begin():
        for category in categories:
            session.merge(category)


def category_getall(user, filter_ids=None, session=None, conf=None):
    session = session or get_session(conf)
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


def category_delete(categories, cascade, session=None, conf=None):
    if categories:
        session = session or get_session(conf)
        with session.begin():
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


def category_delete_by_id(user, filter_ids, cascade, session=None, conf=None):
    if filter_ids:
        session = get_session(conf)
        categories = category_getall(user, filter_ids, session, conf)
        category_delete(categories, cascade, session, conf)


def item_create(items, conf=None):
    if items:
        session = get_session(conf)
        with session.begin():
            session.add_all(items)


def item_update(items, conf=None):
    session = get_session(conf)
    with session.begin():
        for item in items:
            session.merge(item)


def item_getall(user, filter_ids=None, session=None, conf=None):
    session = session or get_session(conf)
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


def item_delete(items, session=None, conf=None):
    session = session or get_session(conf)
    with session.begin():
        for item in items:
            session.delete(item)


def item_delete_by_id(user, filter_ids, conf=None):
    if filter_ids:
        session = get_session(conf)
        items = item_getall(user, filter_ids, session, conf)
        item_delete(items, session, conf)
