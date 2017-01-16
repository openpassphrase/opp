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


def category_create(categories, session=None, conf=None):
    session = session or get_session(conf)
    if categories:
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
                for entry in category.entries:
                    session.delete(entry)
                session.delete(category)
        else:
            for category in categories:
                for entry in category.entries:
                    entry.category_id = None
                    session.add(entry)
                session.delete(category)
        session.commit()


def category_delete_by_id(filter_ids, cascade, session=None, conf=None):
    if filter_ids:
        session = session or get_session(conf)
        categories = category_getall(filter_ids, session, conf)
        category_delete(categories, cascade, session, conf)


def entry_create(entries, session=None, conf=None):
    session = session or get_session(conf)
    if entries:
        session.add_all(entries)
        session.commit()


def entry_update(entries, session=None, conf=None):
    session = session or get_session(conf)
    for entry in entries:
        session.merge(entry)
    session.commit()


def entry_getall(filter_ids=None, session=None, conf=None):
    session = session or get_session(conf)
    if filter_ids:
        query = session.query(
            models.Entry).order_by(
            models.Entry.id).filter(
            models.Entry.id.in_(filter_ids)).outerjoin(
            models.Category)

    else:
        query = session.query(
            models.Entry).order_by(
            models.Entry.id).outerjoin(
            models.Category)
    return query.all()


def entry_delete(entries, session=None, conf=None):
    session = session or get_session(conf)
    for entry in entries:
        session.delete(entry)
    session.commit()


def entry_delete_by_id(filter_ids, session=None, conf=None):
    if filter_ids:
        session = session or get_session(conf)
        entries = entry_getall(filter_ids, session, conf)
        entry_delete(entries, session, conf)
