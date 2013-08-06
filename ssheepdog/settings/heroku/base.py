from ..base import *

import dj_database_url
DATABASES['default'] = dj_database_url.config()

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

S3_BACKEND = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = S3_BACKEND
STATICFILES_STORAGE = S3_BACKEND
COMPRESS_STORAGE = S3_BACKEND

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = 'ssheepdog'

# OpenID settings
LOGIN_URL = '/openid/login/'
OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = False
OPENID_UPDATE_DETAILS_FROM_AX = True
# OPENID_USE_AS_ADMIN_LOGIN = TRUE
OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/site-xrds?hd=%s' % 'sheepdog.com'
AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)
INSTALLED_APPS = list(INSTALLED_APPS) + [
    'django_openid_auth',
    ]
