from datetime import datetime
from sqlalchemy import (Column, DateTime, ForeignKey,
                        Index, Integer, Sequence, String)
from sqlalchemy.orm import relationship

from . import Base


class Entry(Base):

    __tablename__ = 'entries'
    __table_args__ = (Index('category_id_idx', 'category_id'),)

    id = Column(Integer, Sequence('entry_id_seq'), primary_key=True)
    category_id = Column(Integer, Sequence('category_id_seq'),
                         ForeignKey('categories.id'), default=None)
    entry_blob = Column(String(4096), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())

    category = relationship('Category', back_populates='entries')
