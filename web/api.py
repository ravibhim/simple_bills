import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext.ndb import Key
from datetime import date
from api_models import *
from models import *
from utils import *

import settings

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
WEB_CLIENT_ID = settings.WEB_CLIENT_ID

@endpoints.api( name='simplebills',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class SimpleBillApi(remote.Service):

    @endpoints.method(message_types.VoidMessage, ProfileMessage,
            path='getProfile',
            http_method='POST', name='getProfile')
    def getProfile(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
        profile = userProfile(user)

        pm = ProfileMessage()
        pm.userId = profile.userId
        pm.nickname = profile.nickname
        return pm


    @endpoints.method(message_types.VoidMessage, AccountListMessage,
            path='listAccounts',
            http_method='POST', name='listAccounts')
    def listAccounts(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = userProfile(user)
        def _copyAccountsMessage(profile):
            alm = AccountListMessage()
            for accountId in profile.accountIds:
                am = AccountMessage()
                account = Key(Account, accountId).get()
                am.accountId = accountId
                am.name = account.name

                am.check_initialized()
                alm.accounts.append(am)
            alm.check_initialized()
            return alm

        return _copyAccountsMessage(profile)


    @endpoints.method(StringMessage, AccountMessage,
            path='createAccount',
            http_method='POST', name='createAccount')
    def createAccount(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = userProfile(user)
        account_name = request.data

        @ndb.transactional(xg=True)
        def _createAccount(profile, account_name):
            am = AccountMessage()

            account = Account(name = account_name)
            acc_key = account.put()

            profile.accountIds.append(acc_key.id())
            profile.put()

            am.accountId = acc_key.id()
            am.name = account_name

            return am

        return _createAccount(profile, account_name)

    def _checkAccountBelongsToProfile(self, accountId, profile):
        if (accountId not in profile.accountIds):
            raise AccountUnauthorizedAccess("{} tried to access account id {}.".format(profile.key.id(), accountId))


    @endpoints.method(AccountMessage, AccountDetailMessage,
            path='getAccount',
            http_method='POST', name='getAccount')
    def getAccount(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = userProfile(user)
        accountId = int(request.accountId)
        self._checkAccountBelongsToProfile(accountId,profile)

        accountKey = Key(Account, accountId)
        account = accountKey.get()
        bills = Bill.query(ancestor=accountKey).order(-Bill.date)

        adm = AccountDetailMessage()
        am = AccountMessage()
        am.name = account.name
        am.accountId = account.key.id()
        adm.account = am
        adm.bills = []
        for bill in bills:
            bm = BillMessage()
            bm.billId = bill.key.id()
            bm.amount = bill.amount
            bm.date = bill.date.strftime("%d-%m-%Y")
            bm.day = bill.day
            bm.month = bill.month
            bm.year = bill.year
            adm.bills.append(bm)
        adm.check_initialized()

        return adm


    @endpoints.method(BillMessage, BillMessage,
            path='createBill',
            http_method='POST', name='createBill')
    def createBill(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = userProfile(user)
        accountId = int(request.accountId)
        self._checkAccountBelongsToProfile(accountId,profile)

        accountKey = Key(Account, accountId)
        amount = int(request.amount)
        day = int(request.day)
        month = int(request.month)
        year = int(request.year)
        date_prop = date(year,month,day)

        bill = Bill(amount=amount, date=date_prop, parent=accountKey)
        billKey = bill.put()
        bill = billKey.get()

        bm = BillMessage()
        bm.billId = billKey.id()
        bm.amount = bill.amount
        bm.date = str(bill.date)
        bm.day = bill.day
        bm.month = bill.month
        bm.year = bill.year

        return bm


# register API
api = endpoints.api_server([SimpleBillApi])
