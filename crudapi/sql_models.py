import os
import datetime
import uuid

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

eng = create_engine(os.environ['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=eng)

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    email = Column(String, primary_key=True)
    userId = Column(String)
    nickname = Column(String)


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    profileId = Column(String, ForeignKey("profiles.id"))
    name = Column(String)
    tagstr = Column(String)
    defaultCurrencyCode = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    def tags(self):
        return [x.strip().upper() for x in (self.tagstr or '').split(',')]




