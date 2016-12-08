from view_imports import *

class MainPage(BaseHandler):
    def get(self):
        home = '/me'

        if is_user_logged_in(self):
            self.redirect(home)
        else:
            template_values = {
                'login_url': home
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

        accounts_activity = accounts_service.getAccountsActivity().execute()

        template_values = {
            'profile': profile,
            'owner_accounts': response['owner_accounts'] or [],
            'editor_accounts': response['editor_accounts'] or [],
            'supported_currencies': settings.SUPPORTED_CURRENCIES,
            'accounts_activity': accounts_activity
        }

        template = JINJA_ENVIRONMENT.get_template('home.html')
        self.response.out.write(template.render(template_values))

class LogoutPage(BaseHandler):
    def get(self):
        if is_user_logged_in(self):
            revoke_access_token(self)
            self.session['credentials'] = None

        self.redirect('/')

