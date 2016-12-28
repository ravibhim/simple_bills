Development dependencies
------------------------
Install Google Cloud SDK - https://cloud.google.com/sdk/downloads

Install vendor dependencies
------------------------------
pip install -r requirements-vendor.txt -t lib

Run the application locally
---------------------------
dev_appserver.py crudapi/app.yaml web/app.yaml

Setting up Google Cloud Storage python lib
-----------------------------------------
https://cloud.google.com/appengine/docs/python/googlecloudstorageclient/setting-up-cloud-storage
I chose the pip install to install the library in 'lib'

Issue with splitting the endpoints module into multiple modules
--------------------------------------------------------------
https://code.google.com/p/googleappengine/issues/detail?id=11606#makechanges


Running endpoints as a seperate module
--------------------------------------
http://stackoverflow.com/questions/24232580/putting-a-cloud-endpoints-api-in-a-separate-app-engine-module


Running DB Migrations
--------------------------------------
$ cd crudapi
$ pip install alembic pymysql
$ mysql -u root
$ mysql> create database simple_bills;
$ alembic upgrade head
