from django.conf import settings

UPDATE_DETAILS_FROM_SREG = getattr(
    settings, 'OPENID_UPDATE_DETAILS_FROM_SREG', False)

UPDATE_DETAILS_FROM_AX = getattr(
    settings, 'OPENID_UPDATE_DETAILS_FROM_AX', False)

CREATE_USERS = getattr(settings, 'OPENID_CREATE_USERS', False)

LAUNCHPAD_TEAMS_MAPPING_AUTO = getattr(
    settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO', False)

LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST = getattr(
    settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST', [])

LAUNCHPAD_TEAMS_MAPPING = getattr(
    settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})

USE_AS_ADMIN_LOGIN = getattr(settings, 'OPENID_USE_AS_ADMIN_LOGIN', False)

DISALLOW_INAMES = getattr(settings, 'OPENID_DISALLOW_INAMES', False)

REQUIRED_AX_ATTRIBUTES = getattr(settings, "OPENID_REQUIRED_AX_ATTRIBUTES", [
    ('http://axschema.org/contact/email', 'email'),
    ('http://axschema.org/namePerson', 'fullname'),
    ('http://axschema.org/namePerson/first', 'firstname'),
    ('http://axschema.org/namePerson/last', 'lastname'),
    ('http://axschema.org/namePerson/friendly', 'nickname'),
    # The myOpenID provider advertises AX support, but uses
    # attribute names from an obsolete draft of the
    # specification.  We request them for compatibility.
    ('http://schema.openid.net/contact/email', 'old_email'),
    ('http://schema.openid.net/namePerson', 'old_fullname'),
    ('http://schema.openid.net/namePerson/friendly', 'old_nickname')
])

ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS = getattr(
    settings, "ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS", [])

TRUST_ROOT = getattr(settings, 'OPENID_TRUST_ROOT', None)

SSO_SERVER_URL = getattr(settings, 'OPENID_SSO_SERVER_URL', None)