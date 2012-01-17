from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^view_page/$',
       	'ssheepdog.views.view_page'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^results_page/$',
       	'ssheepdog.views.results_page'),
)
