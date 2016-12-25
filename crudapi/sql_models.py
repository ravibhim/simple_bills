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

    @classmethod
    def get(self, id):
        session = Session()
        return session.query(Account).filter(Account.id == id).first()


    def tags(self):
        return [x.strip().upper() for x in (self.tagstr or '').split(',')]


class Bill(Base):
    __tablename__ = 'bills'

    id = Column(String, primary_key=True)
    accountId = Column(String, ForeignKey("accounts.id"))
    title = Column(String)
    amount = Column(Float)
    currency_code = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    date = Column(Date)
    notes = Column(String)

    @classmethod
    def create(self,bill):
        session = Session()
        session.add(bill)
        session.commit()
        session.refresh(bill)

        return bill

    def day(self):
        return self.date.day if self.date else None
    def month(self):
        return self.date.month if self.date else None
    def year(self):
        return self.date.year if self.date else None

