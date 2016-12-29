import sqlalchemy
from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))

    def __repr__(self):
        return ("<User(name='%s', fullname='%s', password='%s')>" %
                (self.name, self.fullname, self.password))


Base.metadata.create_all(engine)


ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')


Session = sessionmaker(bind=engine)
session = Session()
session.add(ed_user)


our_user = session.query(User).filter_by(name='ed').first()
print(ed_user is our_user)
