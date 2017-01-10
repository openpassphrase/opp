from datetime import datetime

from sqlalchemy import (Column, DateTime, ForeignKey,
                        Index, Integer, Sequence, String)
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import relationship


Base = declarative_base()


class Entry(Base):

    __tablename__ = 'entries'
    __table_args__ = (Index('category_id_idx', 'category_id'),)

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True)
    category_id = Column(Integer, Sequence('category_id_seq'),
                         ForeignKey('categories.id'), default=None)
    blob = Column(String(4096), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())

    # category = relationship('Category', back_populates='entries')


class Category(Base):

    __tablename__ = 'categories'

    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    blob = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())
