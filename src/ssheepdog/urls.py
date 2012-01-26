from django.conf.urls.defaults import patterns, url
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
	url(r'^$', 'ssheepdog.views.view_access_summary'),
	url(r'^new_key/$',	'ssheepdog.views.generate_new_application_key'),
	url(r'^sync_keys/$', 'ssheepdog.views.sync_keys'),
	url(r'^user/(?P<id>[0-9]+)/$', 'ssheepdog.views.user_admin_view'),	
	url(r'^login/(?P<id>[0-9]+)/$','ssheepdog.views.login_admin_view'),
    url(r'^login/$', login, {}, name='login'),
    url(r'^logout/$', logout, {}, name='logout'),
)
