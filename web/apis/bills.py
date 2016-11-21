import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from google.appengine.ext.ndb import Key
from datetime import date

import pprint
import cloudstorage as gcs
import os
import uuid

from models import *
from api_messages import *
import settings
from api_utils import *


EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
WEB_CLIENT_ID = settings.WEB_CLIENT_ID

@endpoints.api(name='bills',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class BillsApi(remote.Service):
    @endpoints.method(BillMessage, BillMessage,
            path='createBill',
            http_method='POST', name='createBill')
    def createBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)

        accountKey = Key(Account, accountId)
        amount = int(request.amount)
        date_prop = date(int(request.year),int(request.month),int(request.day))

        # App generated billId
        billId = str(uuid.uuid4())
        # Build filenames from staging_filenames (i.e copy files to GCS and build filenames)
        filepaths = []
        for staging_filepath in request.staging_filepaths:
            filename = os.path.basename(staging_filepath.data)
            filepath = '/' + settings.FILE_BUCKET + '/' + str(accountKey.id())+ '/' + billId + '/' + filename
            filepaths.append(filepath)
            gcs.copy2(staging_filepath.data, filepath)

        bill = Bill(
                id=billId,
                amount=int(request.amount),
                date=date_prop,
                filepaths=filepaths,
                parent=accountKey
                )
        bill.put()
        return buildBillMessage(bill)
