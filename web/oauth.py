import httplib2
import apiclient
import oauth2client

from base import BaseHandler

CLIENT_ID = '1037916704056-t9g7m7vcipm0lpc1l7d39umrq731j8kn.apps.googleusercontent.com'
CLIENT_SECRET = '2BWS2YfcZG1YhLxtHKakn03O'
SCOPE = 'https://www.googleapis.com/auth/userinfo.email'

class OAuth2CallbackPage(BaseHandler):
    def get(self):
        flow = oauth2client.client.OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            prompt='consent',
            #redirect_uri='http://localhost:8080/oauth2callback')
            redirect_uri='https://confrence-central-145321.appspot.com/oauth2callback')
        code = self.request.get('code')

        if not code:
            auth_uri = flow.step1_get_authorize_url()
            return self.redirect(auth_uri)
        else:
            credentials = flow.step2_exchange(self.request.get('code'))
            self.session['credentials'] = credentials.to_json()
            redirect_url = '/'
            if self.session.get('return_url'):
                redirect_url = str(self.session.get('return_url'))
                self.session['redirect_url'] = '/'

            return self.redirect(redirect_url)

def get_service(session):
    credentials = oauth2client.client.OAuth2Credentials.from_json(session.get('credentials'))

    # Build the service object
    #api_root = 'http://localhost:8080/_ah/api'
    api_root = 'https://confrence-central-145321.appspot.com/_ah/api'
    api = 'simplebills'
    version = 'v1'
    discovery_url = '%s/discovery/v1/apis/%s/%s/rest' % (api_root, api, version)
    http_auth = credentials.authorize(httplib2.Http())

    service = apiclient.discovery.build('simplebills', 'v1', discoveryServiceUrl=discovery_url, http=http_auth)
    return service


def check_credentials(func):
    """ Checks whether the session user has valid credentials """
    def wrapper(*args, **kwargs):
        page_handler = args[0]
        page_handler.session['return_url'] = page_handler.request.url

        session_credentials = page_handler.session.get('credentials')
        if not session_credentials:
            return page_handler.redirect('/oauth2callback')

        credentials = oauth2client.client.OAuth2Credentials.from_json(session_credentials)
        if credentials.access_token_expired:
            return page_handler.redirect('/oauth2callback')

        return func(*args, **kwargs)
    return wrapper

