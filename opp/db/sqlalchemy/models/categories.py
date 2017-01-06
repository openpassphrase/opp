from datetime import datetime
from sqlalchemy import Column, DateTime, Index, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Category(Base):

    __tablename__ = 'categories'
    __table_args__ = (Index('created_at_category_idx', 'created_at'),
                      Index('updated_at_category_idx', 'updated_at'))

    id = Column(Integer, Sequence('category_id_seq'), primary_key=True)
    category_blob = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(),
                        nullable=False, onupdate=lambda: datetime.now())
