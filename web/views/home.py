from view_imports import *

class MainPage(BaseHandler):
    def get(self):
        template_values = {
            'login_url': '/me'
        }

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.out.write(template.render(template_values))

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

        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.out.write(template.render(template_values))
