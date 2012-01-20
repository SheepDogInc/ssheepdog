from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^view_page/$', 'ssheepdog.views.view_page'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^results/$',	'ssheepdog.views.results_page', name="results"),
	url(r'^new_key/$',	'ssheepdog.views.generate_new_application_key'),
	url(r'^sync_keys/$', 'ssheepdog.views.sync_keys'),
)
