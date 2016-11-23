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
        template_values = {
                'account': response.get('account'),
                'bills': response.get('bills') or [],
                'accounts': response_accounts.get('accounts') or [],
        }
        path = 'templates/account_detail.html'
        self.response.out.write(template.render(path, template_values))
