import os
import webapp2
from datetime import date
from google.appengine.api import users
from google.appengine.ext.webapp import template
from dateutil import parser

from oauth import *
import settings
from utils import *
from base import BaseHandler

import pprint

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
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        accounts_service = get_service(self.session, 'accounts')
        response = accounts_service.listAccounts().execute()
        accounts = response.get('accounts') or []

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
        path = os.path.join(os.path.dirname(__file__), 'templates/account_detail.html')
        self.response.out.write(template.render(path, template_values))



class CreateBill(BaseHandler):
    def _isFileUploaded(self):
        file_data = self.request.POST['filename']
        return True if file_data != u'' else False

    @check_credentials
    def post(self, account_id):
        # Put the file in GCS first and get the stage filepath
        # Send that info to the API so that it would move the file to the right path
        file_data = self.request.POST['filename']
        pprint.pprint(self._isFileUploaded())
        if self._isFileUploaded():
            staging_filepath = uploadBillImageToStaging(file_data)

        bills_service = get_service(self.session, 'bills')
        bill_date = parser.parse(self.request.get('bill_date'))
        body = {
            'accountId': account_id,
            'desc': self.request.get('bill_desc'),
            'amount': self.request.get('bill_amount'),
            'date': self.request.get('bill_date')
        }
        if self._isFileUploaded():
            body['staging_filepaths'] = [{'data': staging_filepath}]
        pprint.pprint(body)
        response = bills_service.createBill(body=body).execute()

        self.redirect('/account/' + account_id)

class EditBill(BaseHandler):
    @check_credentials
    def get(self, account_id, bill_id):
        profiles_service = get_service(self.session, 'profiles')
        profile = profiles_service.getProfile().execute()

        bills_service = get_service(self.session, 'bills')
        bill = bills_service.getBill(body={'accountId': account_id, 'billId':bill_id}).execute()

        template_values = {
            'profile': profile,
            'account_id': account_id,
            'bill': bill
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/bill_edit.html')
        self.response.out.write(template.render(path, template_values))

    @check_credentials
    def post(self, account_id, bill_id):
        bills_service = get_service(self.session, 'bills')
        bill = bills_service.updateBill(
                body={
                    'accountId': account_id,
                    'billId': bill_id,
                    'desc': self.request.get('bill_desc'),
                    'amount': self.request.get('bill_amount'),
                    'date': self.request.get('bill_date')
                    }
                ).execute()

        self.redirect('/account/' + account_id + '/' + bill_id + '/edit_bill')



config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key-foo',
}

app = webapp2.WSGIApplication([
  #('/test', TestPage),
  ('/', MainPage),
  ('/oauth2callback', OAuth2CallbackPage),
  ('/me', HomePage),
  ('/create_account', CreateAccount),
  ('/account/(\d+)', AccountDetail),
  ('/account/(\d+)/create_bill', CreateBill),
  ('/account/(\d+)/(.*)?/edit_bill', EditBill),
], debug=True, config=config)


def main():
  application.RUN()

if __name__ == '__main__':
  main()
