from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Sequence
from sqlalchemy.orm import relationship

from . import Base
from entries import Entry


class Category(Base):

    __tablename__ = 'categories'

    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    category_blob = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())

    entries = relationship('Entry', order_by=Entry.id,
                           back_populates='categories')
