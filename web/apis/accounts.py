# Ref: https://mail.python.org/pipermail/python-list/2012-January/618880.html
from api_imports import *

@endpoints.api(name='accounts',
                version='v1',
                allowed_client_ids=[WEB_CLIENT_ID, API_EXPLORER_CLIENT_ID],
                scopes=[EMAIL_SCOPE])
class AccountsApi(remote.Service):
    @endpoints.method(message_types.VoidMessage, AccountListMessage,
            path='listAccounts',
            http_method='POST', name='listAccounts')
    def listAccounts(self, request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

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
        user=endpoints.get_current_user()
        raise_unless_user(user)

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

    @endpoints.method(AccountMessage, AccountMessage,
            path='updateAccount',
            http_method='POST', name='updateAccount')
    def updateAccount(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)
        account = Key(Account, accountId).get()
        account.tagstr = request.tagstr
        account.put()

        return self._buildAccountMessage(account)


    @endpoints.method(AccountMessage, AccountMessage,
            path='getAccount',
            http_method='POST', name='getAccount')
    def getAccount(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        profile = userProfile(user)
        accountId = int(request.accountId)
        checkAccountBelongsToUser(user, accountId)

        accountKey = Key(Account, accountId)
        account = accountKey.get()

        return self._buildAccountMessage(account)

    def _buildAccountMessage(self,account):
        accountKey = account.key
        bills = Bill.query(ancestor=accountKey).order(-Bill.date)

        am = AccountMessage()
        am.accountId = account.key.id()
        am.name = account.name
        am.tagstr = account.tagstr
        am.tags = []
        for tag in account.tags():
            sm = StringMessage()
            sm.data = tag
            am.tags.append(sm)
        am.bills = []
        for bill in bills:
            bm = buildBillMessage(bill)
            am.bills.append(bm)

        am.check_initialized()

        return am

    @endpoints.method(message_types.VoidMessage, AccountsActivityMessage,
            path='getAccountsActivity',
            http_method='POST', name='getAccountsActivity')
    def getAccountsActivity(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        profile = userProfile(user)

        asam = AccountsActivityMessage()
        for accountId in profile.accountIds:
            accountKey = Key(Account, accountId)
            account = accountKey.get()

            aam = AccountActivityMessage()
            aam.accountId = accountId
            aam.name = account.name

            # Get Bills from the last 30 days
            bills = Bill.query(ancestor=accountKey).order(-Bill.date)
            bills.filter(Bill.date >= date.today()-timedelta(days=30))

            # Build a hash of date and count
            activity = {}
            for bill in bills:
                bill_date = str(bill.date)
                day_activity = activity.get(bill_date, {'num_bills': 0})
                day_activity['num_bills'] +=1
                activity[bill_date] = day_activity

            for bill_date, value in activity.iteritems():
                # Build DayActivityMessages
                dam = DayActivityMessage()
                dam.date = bill_date
                dam.num_bills = value['num_bills']
                aam.activity.append(dam)

            aam.check_initialized()
            asam.data.append(aam)
        return asam
