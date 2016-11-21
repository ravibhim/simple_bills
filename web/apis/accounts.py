# Ref: https://mail.python.org/pipermail/python-list/2012-January/618880.html

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote
from google.appengine.ext.ndb import Key

import settings
from models import *
from api_messages import *
from api_utils import *

EMAIL_SCOPE = endpoints.EMAIL_SCOPE
API_EXPLORER_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID
WEB_CLIENT_ID = settings.WEB_CLIENT_ID

@endpoints.api(name='accounts',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class AccountsApi(remote.Service):
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

    @endpoints.method(AccountMessage, AccountDetailMessage,
            path='getAccount',
            http_method='POST', name='getAccount')
    def getAccount(self,request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')

        profile = userProfile(user)
        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)

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
            bm = buildBillMessage(bill)
            adm.bills.append(bm)

        adm.check_initialized()

        return adm
