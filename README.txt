Development dependencies
------------------------
Install Google Cloud SDK - https://cloud.google.com/sdk/downloads

Install vendor dependencies
------------------------------
pip install -r requirements-vendor.txt -t lib

Run the application locally
---------------------------
dev_appserver.py  web/
dev_appserver.py  --clear_datastore=yes web/


Deploy to production
--------------------
appcfg.py --no_cookies update web -E SERVER:'https://simplebills-152707.appspot.com' -E WEB_CLIENT_ID:'' -E WEB_CLIENT_SECRET:''

Deploy to test version
----------------------
1) Mark version as 'test' in app.yaml
appcfg.py --no_cookies update web -E SERVER:'https://test-dot-simplebills-152707.appspot.com' -E WEB_CLIENT_ID:'' -E WEB_CLIENT_SECRET:''
