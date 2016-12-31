import webapp2
import os

from base import BaseHandler
from oauth import OAuth2CallbackPage
from views import *


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key-foo',
}

app = webapp2.WSGIApplication([
  #('/test', TestPage),
  ('/', MainPage),
  ('/oauth2callback', OAuth2CallbackPage),
  ('/me', HomePage),
  ('/logout', LogoutPage),
  ('/create_account', CreateAccount),
  ('/account/([^/]*)?', AccountDetail),
  ('/account/(.*)?/settings', AccountSettings),
  ('/account/(.*)?/add_editor', AddEditor),
  ('/account/(.*)?/remove_editor', RemoveEditor),
  ('/account/(.*)?/create_bill', CreateBill),
  ('/account/(.*)?/search_bills', SearchBill),
  ('/account/(.*)?/(.*)?/edit_bill', EditBill),
  ('/account/(.*)?/(.*)?/add_file', AddFileToBill),
  ('/account/(.*)?/(.*)?/(.*)?/remove_file', RemoveFileFromBill),
  ('/account/(.*)?/(.*)?/(.*)?/detect_file_type', DetectBillFileType),
  ('/useinvitation/([^/]*)?', UseInvitation),
], debug=True, config=config)


def main():
  application.RUN()

if __name__ == '__main__':
  main()
