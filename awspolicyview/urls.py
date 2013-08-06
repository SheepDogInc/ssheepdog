from django.conf.urls import patterns, url
from awspolicyview.views import ListAWSPoliciesView

aws_patterns = patterns('awspolicyview.views',
    url(r'^$', ListAWSPoliciesView.as_view(), name='policy_view'),
)