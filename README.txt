Development dependencies
------------------------
Install Google Cloud SDK - https://cloud.google.com/sdk/downloads

Run the application locally
---------------------------
dev_appserver.py  web/

Deploy to production
--------------------
appcfg.py --no_cookies update web -E OAUTH_REDIRECT_URL:'https://confrence-central-145321.appspot.com/oauth2callback' -E API_ROOT:'https://confrence-central-145321.appspot.com/_ah/api'
