from view_imports import *

class CreateAccount(BaseHandler):
    @check_credentials
    def post(self):
        account_name = self.request.get('account_name')

        accounts_service = get_service(self.session, 'accounts')
        response = accounts_service.createAccount(body={'data':account_name}).execute()

        self.redirect('/account/'+response['accountId'])


class AccountDetail(BaseHandler):
    @check_credentials
    def get(self, account_id):
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        account_service = get_service(self.session,'accounts')
        response = account_service.getAccount(body={'accountId':account_id}).execute()
        response_accounts = account_service.listAccounts().execute()
        account_tags = []
        for tag in response['tags']:
            account_tags.append(tag['data'])
        pprint.pprint(account_tags)

        template_values = {
                'account_id': response['accountId'],
                'account_name': response['name'],
                'account_tags': account_tags,
                'bills': response.get('bills') or [],
                'accounts': response_accounts.get('accounts') or [],
        }
        path = 'templates/account_detail.html'
        self.response.out.write(template.render(path, template_values))


class AccountSettings(BaseHandler):
    @check_credentials
    def get(self, account_id):
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        account_service = get_service(self.session,'accounts')
        response = account_service.getAccount(body={'accountId':account_id}).execute()

        response_accounts = account_service.listAccounts().execute()
        template_values = {
                'account_id': account_id,
                'tagstr': response.get('tagstr') or '',
        }

        path = 'templates/account_settings.html'
        self.response.out.write(template.render(path, template_values))

    @check_credentials
    def post(self, account_id):
        account_service = get_service(self.session,'accounts')
        response = account_service.updateAccount(
                body={
                    'accountId': account_id,
                    'tagstr': self.request.get('account_tagstr')
                    }
                ).execute()

        self.redirect(self.request.path)
