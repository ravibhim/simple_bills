import webapp2
import os
from google.appengine.ext.webapp import template

# from utils import *
from base import BaseHandler
from oauth import OAuth2CallbackPage
from views import *

import pprint

class MainPage(BaseHandler):
    def get(self):
        template_values = {
            #'login_url': users.create_login_url('/me')
            'login_url': '/me'
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
        self.response.out.write(template.render(path, template_values))


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
  ('/account/(\d+)/(.*)?/edit_bill', EditBill),
], debug=True, config=config)


def main():
  application.RUN()

if __name__ == '__main__':
  main()
