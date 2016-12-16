import logging
import endpoints
import cloudstorage as gcs

from google.appengine.api import images
from google.appengine.ext import blobstore

from google.appengine.api import users
from google.appengine.ext import ndb

from google.appengine.api import app_identity


import time
import urllib
from datetime import datetime, timedelta
import os
import base64

GCS_ACCESS_ENDPOINT = 'https://storage.googleapis.com'


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

def checkAccountAccess(user, account_id, scope=settings.READ_SCOPE):
    profile = userProfile(user)

    if account_id in profile.accountIds:
        return True

    if (account_id in profile.editorForAccountsIds) and (scope <= settings.UPDATE_SCOPE):
        return True

    raise endpoints.InternalServerErrorException("{} tried to access account id {} with scope {}.".format(profile.key.id(), account_id, scope))

def getFilepath(account_id, bill_id, filename):
    return '/' + account_id + '/' + bill_id + '/' + filename

def copyStagingFilepathsToGcs(request, account_id, bill_id, bill = None):
    filepaths = []
    for staging_filepath in request.staging_filepaths:
        filename = os.path.basename(staging_filepath.data)
        filepath = getFilepath(account_id, bill_id, filename)
        if bill and (filepath in bill.filepaths):
            raise endpoints.InternalServerErrorException("{} file already uploaded.".format(filename))
        filepaths.append(filepath)
        gcs.copy2(
                '/' + settings.STAGING_FILE_BUCKET + staging_filepath.data,
                '/' + settings.FILE_BUCKET + filepath)

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
        #blob_key = blobstore.create_gs_key('/gs' + filepath)
        #img_url = images.get_serving_url(blob_key=blob_key)
        fm.filename = os.path.basename(filepath)
        fm.signed_url= sign_url(filepath)
        bm.files.append(fm)

    return bm

# http://stackoverflow.com/questions/29847759/cloud-storage-and-secure-download-strategy-on-app-engine-gcs-acl-or-blobstore
# We dont have this working in development. Not really needed.
def sign_url(bucket_object, expires_after_seconds=300):
    method = 'GET'
    gcs_filename = '/%s%s' % (settings.FILE_BUCKET, bucket_object)
    content_md5, content_type = None, None

    expiration = datetime.utcnow() + timedelta(seconds=expires_after_seconds)
    expiration = int(time.mktime(expiration.timetuple()))

    # Generate the string to sign.
    signature_string = '\n'.join([
        method,
        content_md5 or '',
        content_type or '',
        str(expiration),
        gcs_filename])

    _, signature_bytes = app_identity.sign_blob(str(signature_string))
    signature = base64.b64encode(signature_bytes)

    # Set the right query parameters.
    query_params = {'GoogleAccessId': app_identity.get_service_account_name(),
                    'Expires': str(expiration),
                    'Signature': signature}

    # Return the download URL.
    return '{endpoint}{resource}?{querystring}'.format(endpoint=GCS_ACCESS_ENDPOINT,
                                                       resource=gcs_filename,
                                                       querystring=urllib.urlencode(query_params))

