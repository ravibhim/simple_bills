import os
import logging

import webapp2
from datetime import date
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

from google.appengine.ext.ndb import Key
from models import Account,Bill, AccountUnauthorizedAccess
from utils import *

class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'login_url': users.create_login_url('/me')
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))


class HomePage(webapp2.RequestHandler):
    def get(self):
        profile = getProfile(users.get_current_user())
        template_values = {
            'profile': profile,
            'accounts': profile.getAccounts()
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/home.html')
        self.response.out.write(template.render(path, template_values))

class CreateAccount(webapp2.RequestHandler):
    @ndb.transactional(xg=True)
    def post(self):
        profile = getProfile(users.get_current_user())
        account_name = self.request.get('account_name')

        account = Account(name = account_name)
        acc_key = account.put()

        profile.accountIds.append(acc_key.id())
        profile.put()

        self.redirect('/account/'+str(acc_key.id()))

class AccountDetail(webapp2.RequestHandler):
    def get(self, account_id):
        user_owns_account_check(users.get_current_user(), int(account_id))

        account_key = Key(Account, int(account_id))
        account = account_key.get()
        bills = Bill.query(ancestor=account_key).order(-Bill.date)
        template_values = {
                'account': account,
                'bills': bills
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/account_detail.html')
        self.response.out.write(template.render(path, template_values))

class CreateBill(webapp2.RequestHandler):
    def post(self, account_id):
        user_owns_account_check(users.get_current_user(), int(account_id))

        account_key = Key(Account, int(account_id))
        amount = int(self.request.get('bill_amount'))
        date_prop = None

        day_str = self.request.get('bill_day')
        month_str = self.request.get('bill_month')
        year_str = self.request.get('bill_year')

        if (day_str != '') and (month_str != '') and (year_str != ''):
            day= int(self.request.get('bill_day'))
            month = int(self.request.get('bill_month'))
            year = int(self.request.get('bill_year'))
            date_prop = date(year, month, day)

        bill = Bill(amount=amount, date = date_prop, parent=account_key)
        bill.put()

        self.redirect('/account/' + str(account_key.id()))




app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/me', HomePage),
  ('/create_account', CreateAccount),
  ('/account/(\d+)', AccountDetail),
  ('/account/(\d+)/create_bill', CreateBill),
], debug=True)


def main():
  application.RUN()


if __name__ == '__main__':
  main()

