from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore

class Account(ndb.Model):
    name = ndb.StringProperty()
    tagstr = ndb.StringProperty(indexed=False)
    default_currency_code = ndb.StringProperty(indexed=False)
    createdAt = ndb.DateTimeProperty(auto_now_add=True, indexed=False)

    def tags(self):
        return [x.strip().upper() for x in (self.tagstr or '').split(',')]



class Bill(ndb.Model):
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

    def img_urls(self, size=''):
        img_urls = []
        for filepath in self.filepaths:
            blob_key = blobstore.create_gs_key('/gs' + filepath)
            img_url = images.get_serving_url(blob_key=blob_key) + size
            img_urls.append(img_url)
        return img_urls

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
