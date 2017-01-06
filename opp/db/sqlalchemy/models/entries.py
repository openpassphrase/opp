from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy import Index, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Entry(Base):

    __tablename__ = 'entries'
    __table_args__ = (Index('category_id_idx', 'category_id'),
                      Index('created_at_entry_idx', 'created_at'),
                      Index('updated_at_entry_idx', 'updated_at'))

    id = Column(Integer(20), Sequence('entry_id_seq'), primary_key=True)
    category_id = Column(Integer, Sequence('category_id_seq'),
                         ForeignKey('categories.id'), default=None)
    entry_blob = Column(String(4096), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())
