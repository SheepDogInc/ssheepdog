from settings import *

# Django secure settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 500
SECURE_FRAME_DENY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
# This is Heroku-specific to get around a weird configuration they have
# Settings is required to prevent redirect loop
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", None)

# OpenID settings
AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = list(INSTALLED_APPS) + [
    'django_openid_auth',
    ]

MIDDLEWARE_CLASSES = ["djangosecure.middleware.SecurityMiddleware",
                      ] + list(MIDDLEWARE_CLASSES)

OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = False
OPENID_UPDATE_DETAILS_FROM_AX = True
# OPENID_USE_AS_ADMIN_LOGIN = TRUE
# OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/site-xrds?ns=2&hd=sheepdoginc.ca'
OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/site-xrds?hd=%s' % 'sheepdoginc.ca'

LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'

STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_QUERYSTRING_AUTH = False
AWS_STORAGE_BUCKET_NAME = 'ssheepdog'
AWS_ACCESS_KEY_ID = os.environ['AWS_KEY']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET']

STATIC_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
