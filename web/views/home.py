from view_imports import *

class HomePage(BaseHandler):
    @check_credentials
    def get(self):
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        accounts_service = get_service(self.session, 'accounts')
        response = accounts_service.listAccounts().execute()
        accounts = response.get('accounts') or []

        accounts_activity = accounts_service.getAccountsActivity().execute()

        template_values = {
            'profile': profile,
            'accounts': accounts,
            'accounts_activity': accounts_activity
        }

        path = 'templates/home.html'
        self.response.out.write(template.render(path, template_values))
