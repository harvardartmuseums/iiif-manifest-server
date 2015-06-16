from django.conf.urls import patterns, url

from manifests import views

urlpatterns = patterns('',
    url(r'^(?P<document_id>[a-z]+:[A-Za-z\d]+)$', views.manifest, name='manifest'),

    url(r'^delete/(?P<document_id>[a-z]+:[A-Za-z\d]+)$', views.delete, name='delete'),

    url(r'^refresh/(?P<document_id>[a-z]+:[A-Za-z\d]+)$', views.refresh, name='refresh'),
    url(r'^refresh/source/(?P<source>[a-z]+)$', views.refresh_by_source, name='refresh_by_source'),
)
