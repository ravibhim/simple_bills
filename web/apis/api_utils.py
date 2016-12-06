import logging
import endpoints
import os
import cloudstorage as gcs

from google.appengine.api import images
from google.appengine.ext import blobstore

from google.appengine.api import users
from google.appengine.ext import ndb

from models import *
from api_messages import *

import settings

def raise_unless_user(user):
    if not user:
        raise endpoints.UnauthorizedException('Authorization required')

def extract_array_from_data_list(list):
    result = []
    for item in list:
        result.append(item.data)

    return result


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

def getFilepath(account_id, bill_id, filename):
    return '/' + settings.FILE_BUCKET + '/' + account_id + '/' + bill_id + '/' + filename

def copyStagingFilepathsToGcs(request, account_id, bill_id, bill = None):
    filepaths = []
    for staging_filepath in request.staging_filepaths:
        filename = os.path.basename(staging_filepath.data)
        filepath = getFilepath(account_id, bill_id, filename)
        if bill and (filepath in bill.filepaths):
            raise endpoints.InternalServerErrorException("{} file already uploaded.".format(filename))
        filepaths.append(filepath)
        gcs.copy2(staging_filepath.data, filepath)

    return filepaths


def buildBillMessage(bill):
    bm = BillMessage()

    bm.billId = bill.key.id()
    bm.desc = bill.desc
    bm.currency_code = bill.currency_code
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

        fm = FileMessage()
        blob_key = blobstore.create_gs_key('/gs' + filepath)
        img_url = images.get_serving_url(blob_key=blob_key)
        fm.filename = os.path.basename(filepath)
        fm.original = img_url + "=s0"
        bm.files.append(fm)

    return bm

