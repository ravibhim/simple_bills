import logging

from google.appengine.api import images
from google.appengine.ext import blobstore

from google.appengine.api import users
from google.appengine.ext import ndb

from models import *
from api_messages import *


def userProfile(user):
    if not user:
        raise users.UserNotFoundError("From userProfile(user)")

    user_email = user.email()
    p_key = ndb.Key(Profile, user_email)
    profile = p_key.get()
    # TODO: Instead use Model.create_or_get to wrap the get/update operation in a transaction.

    if not profile:
        profile = Profile(
            key = p_key,
            userId = user.user_id(),
            nickname = user.nickname()
        )
        logging.info('METRIC:USER_ADD - {}'.format(user_email))
        profile.put()

    return profile

def checkAccountBelongsToUser(user, account_id):
    profile = userProfile(user)
    if (account_id not in profile.accountIds):
        raise AccountUnauthorizedAccess("{} tried to access account id {}.".format(profile.key.id(), account_id))


def buildBillMessage(bill):
    bm = BillMessage()

    bm.billId = bill.key.id()
    bm.desc = bill.desc
    bm.amount = bill.amount
    bm.date = str(bill.date)
    bm.day = bill.day
    bm.month = bill.month
    bm.year = bill.year

    for tag in bill.tags:
        sm = StringMessage()
        sm.data = tag
        bm.tags.append(sm)

    for filepath in bill.filepaths:
        sm = StringMessage()
        sm.data = filepath
        bm.filepaths.append(sm)

        im = ImageMessage()
        blob_key = blobstore.create_gs_key('/gs' + filepath)
        img_url = images.get_serving_url(blob_key=blob_key)
        im.original = img_url + "=s0"
        bm.img_urls.append(im)

    return bm

