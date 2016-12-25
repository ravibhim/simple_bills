from api_imports import *

import os
import uuid
import cloudstorage as gcs

from google.appengine.api import taskqueue

@endpoints.api(name='bills',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class BillsApi(remote.Service):
    @endpoints.method(BillMessage, BillMessage,
            path='createBill',
            http_method='POST', name='createBill')
    @ndb.transactional(xg=True)
    def createBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = request.accountId
        checkAccountAccess(user, accountId, settings.UPDATE_SCOPE)

        bill = Bill(
                id=str(uuid.uuid4()),
                accountId=accountId,
                title=request.title,
                currency_code=request.currency_code,
                amount=float(request.amount),
                date=parser.parse(request.date),
                notes=request.notes,
                tagsHashString=arrayToHashString(extractArrayFromStringMessageArray(request.tags))
                )

        bill = Bill.create(bill)

        #self._saveBillFiles(request, billId)
        return buildBillMessage(bill)

    def _saveBillFiles(self,request, billId):
        accountId = request.accountId

        for staging_filepath in request.staging_filepaths:
            billFileId = str(uuid.uuid4())
            # Copy to GCS and get the path
            filepath = copyStagingFilepathToGcs(staging_filepath, str(request.accountId), billId, billFileId)
            billFile = BillFile(
              id=billFileId,
              name=os.path.basename(filepath),
              path=filepath,
              timestamp=datetime.now(),
              parent=ndb.Key('Account', int(accountId), 'Bill', billId)
            )
            #billFile.put()

            # Detect file type
            filepath = getFilepath(str(accountId), billId, billFileId, billFile.name)
            filestat = gcs.stat('/' + settings.FILE_BUCKET + filepath)

            billFile.file_type = filestat.content_type
            billFile.put()


    @endpoints.method(BillMessage, BillMessage,
            path='updateBill',
            http_method='POST', name='updateBill')
    def updateBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.UPDATE_SCOPE)
        accountKey = Key(Account, accountId)

        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)

        bill = billKey.get()
        bill.currency_code = request.currency_code
        bill.amount = float(request.amount)
        bill.desc = request.desc
        bill.date = parser.parse(request.date)
        bill.tags = extractArrayFromStringMessageArray(request.tags)

        bill.put()
        return buildBillMessage(bill)


    @endpoints.method(BillMessage, BillMessage,
            path='addFileToBill',
            http_method='POST', name='addFileToBill')
    def addFileToBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.UPDATE_SCOPE)
        accountKey = Key(Account, accountId)

        billId = request.billId
        bill = Key(Bill, billId, parent=accountKey).get()

        self._saveBillFiles(request,billId)
        return buildBillMessage(bill)

    @endpoints.method(BillMessage, BillMessage,
            path='removeFileFromBill',
            http_method='POST', name='removeFileFromBill')
    def removeFileFromBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.UPDATE_SCOPE)
        accountKey = Key(Account, accountId)

        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)

        billfileId = request.billfileToDeleteId
        billFileKey = Key(BillFile, billfileId, parent=billKey)
        billFileKey.delete()

        return buildBillMessage(billKey.get())


    @endpoints.method(BillMessage, BillMessage,
            path='getBill',
            http_method='POST', name='getBill')
    def getBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.UPDATE_SCOPE)
        accountKey = ndb.Key(Account, accountId)

        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)
        bill = billKey.get()

        return buildBillMessage(bill)


# Not really being used. Not sure how to post to an endpoint directly using a task queue.
    @endpoints.method(BillMessage, StringMessage,
            path='detectBillFileType',
            http_method='POST', name='detectBillFileType')
    def detectBillFileType(self,request):
        accountId = int(request.accountId)
        accountKey = Key(Account, accountId)
        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)

        billfileId = request.billfileToDetect
        billFile = Key(BillFile, billfileId, parent=billKey).get()

        # Build file path
        filepath = getFilepath(str(accountId), billId, billfileId, billFile.name)
        filestat = gcs.stat('/' + settings.FILE_BUCKET + filepath)

        billFile.file_type = filestat.content_type
        billFile.put()

        return StringMessage(data = 'Detected:' + billFile.file_type)
