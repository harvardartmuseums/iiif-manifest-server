from django.urls import re_path

from collections_iiif import views

urlpatterns = [
    re_path(r'^top', views.top, name='top'),
    re_path(r'^(?P<document_type>(object))$', views.collection, name='collection'),
]
