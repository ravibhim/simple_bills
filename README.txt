Development dependencies
------------------------
Install Google Cloud SDK - https://cloud.google.com/sdk/downloads

Install vendor dependencies
------------------------------
pip install -r requirements-vendor.txt -t lib

Run the application locally
---------------------------
dev_appserver.py  web/

Deploy to production
--------------------
appcfg.py --no_cookies update web -E SERVER:'https://confrence-central-145321.appspot.com'

Deploy to test version
----------------------
appcfg.py --no_cookies update web -E SERVER:'https://test-dot-confrence-central-145321.appspot.com'
