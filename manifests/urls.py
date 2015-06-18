from django.conf.urls import patterns, url

from manifests import views

urlpatterns = patterns('',
    url(r'^(?P<document_type>(object))/(?P<document_id>[A-Za-z\d]+)$', views.manifest, name='manifest'),

    url(r'^delete/(?P<document_type>(object))/(?P<document_id>[A-Za-z\d]+)$', views.delete, name='delete'),

    url(r'^refresh/(?P<document_type>(object))/(?P<document_id>[A-Za-z\d]+)$', views.refresh, name='refresh'),
    url(r'^refresh/all/(?P<document_type>(object))$', views.refresh_by_source, name='refresh_by_source'),
)
