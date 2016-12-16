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

        def _copyAccountMessage(accountId):
            am = AccountMessage()
            account = Key(Account, accountId).get()
            am.accountId = accountId
            am.name = account.name

            am.check_initialized()
            return am

        alm = AccountListMessage()
        for accountId in profile.accountIds:
            alm.owner_accounts.append(_copyAccountMessage(accountId))

        for accountId in profile.editorForAccountsIds:
            alm.editor_accounts.append(_copyAccountMessage(accountId))

        alm.check_initialized()
        return alm

    @endpoints.method(AccountMessage, AccountMessage,
            path='createAccount',
            http_method='POST', name='createAccount')
    def createAccount(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        profile = userProfile(user)
        account_name = request.name

        @ndb.transactional(xg=True)
        def _createAccount(profile, account_name, tagstr, default_currency_code):
            am = AccountMessage()

            account = Account(
                    name = account_name,
                    tagstr = tagstr,
                    default_currency_code = default_currency_code
                    )
            acc_key = account.put()

            profile.accountIds.append(acc_key.id())
            profile.put()

            am.accountId = acc_key.id()
            am.name = account_name
            return am

        return _createAccount(profile, request.name, request.tagstr, request.default_currency_code)


    @endpoints.method(AccountMessage, AccountMessage,
            path='updateAccount',
            http_method='POST', name='updateAccount')
    def updateAccount(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.FULL_SCOPE)

        account = Key(Account, accountId).get()
        account.tagstr = request.tagstr
        account.name = request.name
        account.default_currency_code = request.default_currency_code

        account.put()

        return self._buildAccountMessage(account)

    @endpoints.method(AccountMessage, AccountMessage,
            path='addEditor',
            http_method='POST', name='addEditor')
    @ndb.transactional(xg=True)
    def addEditor(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.FULL_SCOPE)

        editor = request.editorToAdd
        editor_profile = Profile.get_by_id(editor)
        if not editor_profile:
            raise endpoints.InternalServerErrorException("Profile with email {} not found.".format(editor))

        account = Key(Account, accountId).get()
        if not editor in account.editors:
            account.editors.append(editor)
            account.put()

        if not accountId in editor_profile.editorForAccountsIds:
            editor_profile.editorForAccountsIds.append(accountId)
            editor_profile.put()

        return self._buildAccountMessage(account)

    @endpoints.method(AccountMessage, AccountMessage,
            path='removeEditor',
            http_method='POST', name='removeEditor')
    @ndb.transactional(xg=True)
    def removeEditor(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId, settings.FULL_SCOPE)

        editor = request.editorToRemove
        editor_profile = Profile.get_by_id(editor)
        if not editor_profile:
            raise endpoints.InternalServerErrorException("Profile with email {} not found.".format(editor))

        account = Key(Account, accountId).get()
        if editor in account.editors:
            account.editors.remove(editor)
            account.put()

        if accountId in editor_profile.editorForAccountsIds:
            editor_profile.editorForAccountsIds.remove(accountId)
            editor_profile.put()

        return self._buildAccountMessage(account)


    @endpoints.method(AccountMessage, AccountMessage,
            path='getAccount',
            http_method='POST', name='getAccount')
    def getAccount(self,request):
        user=endpoints.get_current_user()
        raise_unless_user(user)

        accountId = int(request.accountId)
        checkAccountAccess(user, accountId)

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
        am.default_currency_code = account.default_currency_code
        am.editors = buildStringMessagesFromArray(account.editors)
        am.tags = buildStringMessagesFromArray(account.tags())

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
            bills = bills.filter(Bill.date >= date.today()-timedelta(days=30))

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
