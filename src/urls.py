from django.conf.urls.defaults import patterns, include, url
import ssheepdog.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
	url(r'^', include(ssheepdog.urls)),
)
