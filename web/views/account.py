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
        has_bills = True if 'bills' in response else False

        response_accounts = account_service.listAccounts().execute()
        account_tags = []
        for tag in response['tags']:
            account_tags.append(tag['data'])

        template_values = {
                'profile' : profile,
                'account_id': response['accountId'],
                'account_name': response['name'],
                'account_tags': ",".join(account_tags),
                'has_bills': has_bills,
                'supported_currencies': settings.SUPPORTED_CURRENCIES,
                'account_default_currency_code': response.get('default_currency_code'),
                'accounts': response_accounts.get('accounts') or [],
        }
        template = JINJA_ENVIRONMENT.get_template('account_detail.html')
        self.response.out.write(template.render(template_values))

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
                'name': response.get('name'),
                'tagstr': response.get('tagstr') or '',
                'supported_currencies': settings.SUPPORTED_CURRENCIES,
                'default_currency_code': response.get('default_currency_code') or '',
        }

        template = JINJA_ENVIRONMENT.get_template('account_settings.html')
        self.response.out.write(template.render(template_values))

    @check_credentials
    def post(self, account_id):
        account_service = get_service(self.session,'accounts')
        response = account_service.updateAccount(
                body={
                    'accountId': account_id,
                    'name': self.request.get('account_name'),
                    'tagstr': self.request.get('account_tagstr'),
                    'default_currency_code': self.request.get('account_default_currency_code')
                    }
                ).execute()

        self.redirect(self.request.path)
