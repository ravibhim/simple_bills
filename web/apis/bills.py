from api_imports import *

import os
import uuid

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

        tags = []
        for tag in request.tags:
            if tag.data:
                tags.append(tag.data)

        # App generated billId
        billId = str(uuid.uuid4())

        # Build filenames from staging_filenames (i.e copy files to GCS and build filenames)
        filepaths = copyStagingFilepathsToGcs(request, str(request.accountId), billId)

        bill = Bill(
                id=billId,
                desc=request.desc,
                currency_code=request.currency_code,
                amount=float(request.amount),
                date=parser.parse(request.date),
                tags=tags,
                filepaths=filepaths,
                parent=accountKey
                )
        bill.put()
        return buildBillMessage(bill)


    @endpoints.method(BillMessage, BillMessage,
            path='updateBill',
            http_method='POST', name='updateBill')
    def updateBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)
        accountKey = Key(Account, accountId)

        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)

        bill = billKey.get()
        bill.currency_code = request.currency_code
        bill.amount = float(request.amount)
        bill.desc = request.desc
        bill.date = parser.parse(request.date)

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
        checkAccountBelongsToUser(user, accountId)
        accountKey = Key(Account, accountId)

        billId = request.billId
        bill = Key(Bill, billId, parent=accountKey).get()

        filepaths = copyStagingFilepathsToGcs(request, str(request.accountId), billId, bill)

        bill.filepaths.extend(filepaths)

        bill.put()
        return buildBillMessage(bill)



    @endpoints.method(BillMessage, BillMessage,
            path='getBill',
            http_method='POST', name='getBill')
    def getBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)
        accountKey = ndb.Key(Account, accountId)

        billId = request.billId
        billKey = Key(Bill, billId, parent=accountKey)
        bill = billKey.get()

        return buildBillMessage(bill)

