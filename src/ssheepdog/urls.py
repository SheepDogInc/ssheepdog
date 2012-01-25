from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
	url(r'^$', 'ssheepdog.views.view_access_summary'),
	url(r'^new_key/$',	'ssheepdog.views.generate_new_application_key'),
	url(r'^sync_keys/$', 'ssheepdog.views.sync_keys'),
)
