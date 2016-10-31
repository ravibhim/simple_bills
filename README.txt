Deploy to production

appcfg.py --no_cookies update web -E OAUTH_REDIRECT_URL:'https://confrence-central-145321.appspot.com/oauth2callback' -E API_ROOT:'https://confrence-central-145321.appspot.com/_ah/api'
