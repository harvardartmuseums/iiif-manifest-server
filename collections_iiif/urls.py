from django.conf.urls import patterns, url

from collections_iiif import views

urlpatterns = patterns('',
    url(r'^(?P<document_type>(object))$', views.collection, name='collection'),
)
