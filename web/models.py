from google.appengine.ext import ndb

class Account(ndb.Model):
    name = ndb.StringProperty()
    createdAt = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

class Bill(ndb.Model):
    amount = ndb.IntegerProperty()
    createdAt = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    date = ndb.DateProperty()

    day = ndb.ComputedProperty(lambda self: self.date.weekday() if self.date else None)
    month = ndb.ComputedProperty(lambda self: self.date.month if self.date else None)
    year = ndb.ComputedProperty(lambda self: self.date.year if self.date else None)

class Profile(ndb.Model):
    userId = ndb.StringProperty()
    nickname = ndb.StringProperty()
    accountIds = ndb.IntegerProperty(repeated=True)

    def getAccounts(self):
        return [ndb.Key(Account, account_id).get() for index, account_id in enumerate(self.accountIds)]

class AccountUnauthorizedAccess(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
