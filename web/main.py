import os
import logging
import pprint

import webapp2
from datetime import date
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from api_models import *
from oauth import *

import settings


CLIENT_ID = '1037916704056-t9g7m7vcipm0lpc1l7d39umrq731j8kn.apps.googleusercontent.com'
CLIENT_SECRET = '2BWS2YfcZG1YhLxtHKakn03O'
SCOPE = 'https://www.googleapis.com/auth/userinfo.email'
USER_AGENT = 'my-cmdline-tool/1.0'
OAUTH_DISPLAY_NAME = 'My Commandline Tool'


from google.appengine.ext.ndb import Key
from models import Account,Bill, AccountUnauthorizedAccess
from utils import *
from base import BaseHandler

class MainPage(BaseHandler):
    def get(self):
        template_values = {
            #'login_url': users.create_login_url('/me')
            'login_url': '/me'
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))



class HomePage(BaseHandler):
    @check_credentials
    def get(self):
        service = get_service(self.session)

        profile = service.getProfile().execute()

        response = service.listAccounts().execute()
        accounts = response['accounts']

        template_values = {
            'profile': profile,
            'accounts': accounts
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
        self.response.out.write(template.render(path, template_values))

class CreateAccount(BaseHandler):
    @check_credentials
    def post(self):
        account_name = self.request.get('account_name')

        service = get_service(self.session)
        response = service.createAccount(body={'data':account_name}).execute()

        self.redirect('/account/'+response['accountId'])


class AccountDetail(BaseHandler):
    @check_credentials
    def get(self, account_id):
        service = get_service(self.session)
        profile = service.getProfile().execute()
        response = service.getAccount(body={'accountId':account_id}).execute()

        template_values = {
                'account': response.get('account'),
                'bills': response.get('bills') or []
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/account_detail.html')
        self.response.out.write(template.render(path, template_values))



class CreateBill(BaseHandler):
    @check_credentials
    def post(self, account_id):

        service = get_service(self.session)
        body = {
            'accountId': account_id,
            'amount': self.request.get('bill_amount'),
            'day': self.request.get('bill_day'),
            'month': self.request.get('bill_month'),
            'year': self.request.get('bill_year'),
        }
        response = service.createBill(body=body).execute()

        self.redirect('/account/' + account_id)



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key-foo',
}

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/oauth2callback', OAuth2CallbackPage),
  ('/me', HomePage),
  ('/create_account', CreateAccount),
  ('/account/(\d+)', AccountDetail),
  ('/account/(\d+)/create_bill', CreateBill),
], debug=True, config=config)


def main():
  application.RUN()


if __name__ == '__main__':
  main()

