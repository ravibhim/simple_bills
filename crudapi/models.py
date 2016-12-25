from google.appengine.ext import ndb

class AccountX(ndb.Model):
    name = ndb.StringProperty()
    tagstr = ndb.StringProperty(indexed=False)
    default_currency_code = ndb.StringProperty(indexed=False)
    createdAt = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    editors = ndb.StringProperty(indexed=False, repeated=True)

    def tags(self):
        return [x.strip().upper() for x in (self.tagstr or '').split(',')]


class BillX(ndb.Model):
    desc = ndb.StringProperty()
    currency_code = ndb.StringProperty(indexed=False)
    amount = ndb.FloatProperty()
    createdAt = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    date = ndb.DateProperty()
    filepaths = ndb.StringProperty(repeated=True, indexed=False)
    tags = ndb.StringProperty(repeated=True)

    day = ndb.ComputedProperty(lambda self: self.date.day if self.date else None)
    month = ndb.ComputedProperty(lambda self: self.date.month if self.date else None)
    year = ndb.ComputedProperty(lambda self: self.date.year if self.date else None)

class BillFileX(ndb.Model):
    name = ndb.StringProperty(indexed=False)
    path = ndb.StringProperty(indexed=False)
    file_type = ndb.StringProperty(indexed=False)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

class ProfileX(ndb.Model):
    userId = ndb.StringProperty()
    nickname = ndb.StringProperty()
    accountIds = ndb.IntegerProperty(indexed=False, repeated=True)
    editorForAccountsIds = ndb.IntegerProperty(indexed=False,repeated=True)

    def getAccounts(self):
        return [ndb.Key(Account, account_id).get() for index, account_id in enumerate(self.accountIds)]

# TODO: Use a standard cloud endpoint exception as documented on https://cloud.google.com/appengine/docs/python/endpoints/exceptions
class AccountUnauthorizedAccess(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)
