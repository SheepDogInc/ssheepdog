from settings import INSTALLED_APPS as INSTALLED_APPS_
from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# OpenID settings
AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

INSTALLED_APPS = list(INSTALLED_APPS_) + [
    'django_openid_auth',
    ]

OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = False
OPENID_UPDATE_DETAILS_FROM_AX = True
# OPENID_USE_AS_ADMIN_LOGIN = TRUE
# OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/site-xrds?ns=2&hd=sheepdoginc.ca'
OPENID_SSO_SERVER_URL = 'https://www.google.com/accounts/o8/site-xrds?hd=%s' % 'sheepdoginc.ca'

LOGIN_URL = '/openid/login/'
LOGIN_REDIRECT_URL = '/'

