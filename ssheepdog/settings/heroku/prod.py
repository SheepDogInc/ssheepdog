from .base import *

DEBUG = False
CRISPY_FAIL_SILENTLY = False

AWS_LOCATION = 'prod'
STATIC_URL = 'https://%s.s3.amazonaws.com/%s/' % (
    AWS_STORAGE_BUCKET_NAME, AWS_LOCATION)
