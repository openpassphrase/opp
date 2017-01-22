from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from opp.common import opp_config
from opp.db import models


def get_session(conf=None):
    conf = conf or opp_config.OppConfig()
    engine = create_engine(conf['sql_connect'])
    session_factory = sessionmaker(engine)
    Session = scoped_session(session_factory)
    return Session()


def user_create(user, session=None, conf=None):
    if user:
        session = session or get_session(conf)
        session.add(user)
        session.commit()


def user_update(user, session=None, conf=None):
    if user:
        session = session or get_session(conf)
        session.merge(user)
        session.commit()


def user_get_by_id(id, session=None, conf=None):
    if id:
        session = session or get_session(conf)
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
        session.delete(user)
        session.commit()


def user_delete_by_username(username, session=None, conf=None):
    if username:
        session = session or get_session(conf)
        user = user_get_by_username(username, session, conf)
        user_delete(user, session, conf)


def category_create(categories, session=None, conf=None):
    if categories:
        session = session or get_session(conf)
        session.add_all(categories)
        session.commit()


def category_update(categories, session=None, conf=None):
    session = session or get_session(conf)
    for category in categories:
        session.merge(category)
    session.commit()


def category_getall(filter_ids=None, session=None, conf=None):
    session = session or get_session(conf)
    if filter_ids:
        query = session.query(models.Category).order_by(
            models.Category.id).filter(
            models.Category.id.in_(filter_ids))
    else:
        query = session.query(models.Category).order_by(models.Category.id)
    return query.all()


def category_delete(categories, cascade, session=None, conf=None):
    if categories:
        session = session or get_session(conf)
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
        session.commit()


def category_delete_by_id(filter_ids, cascade, session=None, conf=None):
    if filter_ids:
        session = session or get_session(conf)
        categories = category_getall(filter_ids, session, conf)
        category_delete(categories, cascade, session, conf)


def item_create(items, session=None, conf=None):
    if items:
        session = session or get_session(conf)
        session.add_all(items)
        session.commit()


def item_update(items, session=None, conf=None):
    session = session or get_session(conf)
    for item in items:
        session.merge(item)
    session.commit()


def item_getall(filter_ids=None, session=None, conf=None):
    session = session or get_session(conf)
    if filter_ids:
        query = session.query(
            models.Item).order_by(
            models.Item.id).filter(
            models.Item.id.in_(filter_ids)).outerjoin(
            models.Category)

    else:
        query = session.query(
            models.Item).order_by(
            models.Item.id).outerjoin(
            models.Category)
    return query.all()


def item_delete(items, session=None, conf=None):
    session = session or get_session(conf)
    for item in items:
        session.delete(item)
    session.commit()


def item_delete_by_id(filter_ids, session=None, conf=None):
    if filter_ids:
        session = session or get_session(conf)
        items = item_getall(filter_ids, session, conf)
        item_delete(items, session, conf)
