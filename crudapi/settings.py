import os

SUPPORTED_CURRENCIES = ['INR', 'USD']
SUPPORTED_IMAGE_FILE_TYPES = [
        'image/png'
        ]

READ_SCOPE = 1
EDITOR_SCOPE = 2
FULL_SCOPE = 3 # Can delete too


WEB_CLIENT_ID = os.environ['WEB_CLIENT_ID']
WEB_CLIENT_SECRET = os.environ['WEB_CLIENT_SECRET']

FILE_BUCKET = os.environ['FILE_BUCKET']
STAGING_FILE_BUCKET = os.environ['STAGING_FILE_BUCKET']
