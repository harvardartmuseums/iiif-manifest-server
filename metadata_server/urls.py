from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^collections/', include('collections_iiif.urls')),
    url(r'^manifests/', include('manifests.urls')),
    url(r'^viewers/', include('viewers.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
