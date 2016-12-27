import os
import datetime
import uuid

from sqlalchemy import *
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.event import listen

import pprint
import settings


Base = declarative_base()

eng = create_engine(
        os.environ['SQLALCHEMY_DATABASE_URI'],
        pool_size=15,
        pool_recycle=300
        )
Session = scoped_session(sessionmaker(bind=eng))

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    email = Column(String, primary_key=True)
    userId = Column(String)
    nickname = Column(String)

    Accounts = relationship("Account", order_by="Account.createdAt")
    roleAccounts = relationship("Account", secondary='account_profile_roles')

    @classmethod
    def get(self, email):
        session = Session()
        result = session.query(Profile).filter(Profile.email == email).first()
        session.close()
        return result

    def ownsAccount(self,account):
        return account.profileId == self.id

    def editorOfAccount(self, account, scope):
        result = False
        if scope <= settings.EDITOR_SCOPE:
            session = Session()
            thisProfile = session.query(Profile).filter(Profile.id == self.id).first()
            role = (session.query(AccountProfileRole)
                    .filter(AccountProfileRole.profileId == self.id)
                    .filter(AccountProfileRole.accountId == account.id)
                    .filter(AccountProfileRole.role == 'EDITOR')
                    .first()
                   )
            if role:
                result = True

            session.close()
        return result

class AccountProfileRole(Base):
    __tablename__ = 'account_profile_roles'

    id = Column(Integer, primary_key=True)
    profileId = Column(String, ForeignKey("profiles.id"))
    accountId = Column(String, ForeignKey("accounts.id"))
    role = Column(String)

    @classmethod
    def create(self, accountProfileRole):
        session = Session()
        session.add(accountProfileRole)
        session.commit()
        session.close()

class Account(Base):
    __tablename__ = 'accounts'

    id = Column(String, primary_key=True, default=str(uuid.uuid4()))
    profileId = Column(String, ForeignKey("profiles.id"))
    name = Column(String)
    tagstr = Column(String)
    defaultCurrencyCode = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    Profile = relationship("Profile")
    roleProfiles = relationship("Profile", secondary='account_profile_roles')

    @classmethod
    def create(self, account):
        session = Session()
        session.add(account)
        session.commit()
        session.refresh(account)
        session.close()
        return account

    @classmethod
    def get(self, id):
        session = Session()
        result = session.query(Account).filter(Account.id == id).first()
        session.close()
        return result

    def addEditor(self,profile):
        if profile.email not in self.editors():
            AccountProfileRole.create(
                    AccountProfileRole(
                        profileId = profile.id,
                        accountId = self.id,
                        role = 'EDITOR'
                        )
                    )

    def removeEditor(self,email):
        session = Session()
        profile = session.query(Profile).filter(Profile.email == email).first()
        role = (session.query(AccountProfileRole)
                .filter(AccountProfileRole.profileId == profile.id)
                .filter(AccountProfileRole.accountId == self.id)
                .filter(AccountProfileRole.role == 'EDITOR')
                .first()
               )

        if role:
            session.delete(role)
            session.commit()
        session.close()


    def editors(self):
        session = Session()
        thisAccount = session.query(Account).filter(Account.id == self.id).first()
        result = [x.email for x in thisAccount.roleProfiles]
        session.close()
        return result


    def tags(self):
        return [x.strip().upper() for x in (self.tagstr or '').split(',')]

    def lastNDayBills(self,n):
        session = Session()
        result = (
                session.query(Bill)
                .filter(Bill.accountId == self.id)
                .filter(Bill.date >= datetime.date.today()-datetime.timedelta(days=n))
            )
        session.close()
        return result

    def year_bill_counts(self):
        session = Session()
        result = dict(session.query(Bill.year, func.count(Bill.year))
                    .filter(Bill.accountId == self.id)
                    .group_by(Bill.year)
                    .all()
                  )
        session.close()
        return result

    def month_bill_counts(self,year):
        session = Session()
        result = dict(Session().query(Bill.month, func.count(Bill.month))
                    .filter(Bill.accountId == self.id)
                    .filter(Bill.year == year)
                    .group_by(Bill.month)
                    .all()
                  )
        session.close()
        return result

    def search_bills(self, start_date, end_date, tags,query):
        session = Session()
        result = (
                Session().query(Bill)
                .filter(Bill.accountId == self.id)
                .filter(Bill.date >= start_date)
                .filter(Bill.date <= end_date)
            )
        if len(tags):
            tags_likes = ["%##{}##%".format(tag) for tag in tags]
            result = result.filter(
                        or_(*[Bill.tagsHashString.like(tags_like) for tags_like in tags_likes])
                    )
        if query:
            result = result.filter(Bill.title.ilike("%{}%".format(query)))


        session.close()
        return result

def save_date_fields(mapper, connect, target):
    target.save_date_fields()


class Bill(Base):
    __tablename__ = 'bills'

    id = Column(String, primary_key=True)
    accountId = Column(String, ForeignKey("accounts.id"))
    title = Column(String)
    amount = Column(Float)
    currency_code = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)
    date = Column(Date)
    day = Column(Integer)
    month = Column(Integer)
    year = Column(Integer)
    notes = Column(String)
    tagsHashString = Column(String)

    BillFiles = relationship("BillFile", lazy='subquery', order_by='BillFile.createdAt')

    def save_date_fields(self):
        self.day = self.date.day
        self.month = self.date.month
        self.year = self.date.year

    @classmethod
    def create(self,bill):
        session = Session()
        session.add(bill)
        session.commit()
        session.refresh(bill)
        session.close()
        return bill

    @classmethod
    def createWithFiles(self,bill, billFiles):
        session = Session()
        session.add(bill)
        for billFile in billFiles:
            session.add(billFile)
        session.commit()
        session.refresh(bill)
        session.close()
        return bill


    @classmethod
    def get(self,account_id,bill_id):
        session = Session()
        result = (
                session.query(Bill)
                .filter(Bill.accountId == account_id)
                .filter(Bill.id == bill_id)
                .first()
            )
        session.close()
        return result

    def addFiles(self,billFiles):
        session = Session()
        for billFile in billFiles:
            session.add(billFile)
        session.commit()
        session.close()

    def removeFile(self,billFileId):
        billFile = BillFile.get(self.id, billFileId)
        session = Session()
        session.delete(billFile)
        session.commit()
        session.close()


    def tags(self):
        return hashStringToArray(self.tagsHashString)

listen(Bill, 'before_insert', save_date_fields)

class BillFile(Base):
    __tablename__ = 'bill_files'
    id = Column(String, primary_key=True)
    billId = Column(String, ForeignKey("bills.id"))
    name = Column(String)
    path = Column(String)
    file_type = Column(String)
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

    Bill = relationship("Bill")

    @classmethod
    def get(self, billId, billFileId):
        session = Session()
        result = (
                session.query(BillFile)
                .filter(BillFile.billId == billId)
                .filter(BillFile.id == billFileId)
                .first()
            )
        session.close()
        return result
