import threading

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from opp.common import opp_config
from opp.db import models


_ENGINE = None
_LOCK = threading.Lock()


def get_engine(conf=None):
    conf = conf or opp_config.OppConfig()
    sql_connect = conf['sql_connect']
    global _LOCK, _ENGINE
    if _ENGINE is None:
        with _LOCK:
            if _ENGINE is None:
                _ENGINE = create_engine(sql_connect)
    return _ENGINE


def get_session(conf=None):
    Session = sessionmaker(bind=get_engine(conf))
    return Session()


def category_getall(session=None, conf=None):
    session = session or get_session(conf)
    import pdb;pdb.set_trace()
    query = session.query(models.Category).order_by(models.Category.id)
    return query.all()
