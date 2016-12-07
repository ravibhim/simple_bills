import webapp2
import os

from base import BaseHandler
from oauth import OAuth2CallbackPage
from views import *

import pprint


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
  ('/account/(\d+)/settings', AccountSettings),
  ('/account/(\d+)/create_bill', CreateBill),
  ('/account/(\d+)/search_bills', SearchBill),
  ('/account/(\d+)/(.*)?/edit_bill', EditBill),
  ('/account/(\d+)/(.*)?/add_file', AddFileToBill),
  ('/account/(\d+)/(.*)?/remove_file', RemoveFileFromBill),
], debug=True, config=config)


def main():
  application.RUN()

if __name__ == '__main__':
  main()
