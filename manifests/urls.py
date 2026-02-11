from django.urls import re_path

from manifests import views

urlpatterns = [
    re_path(r'^(?P<document_type>(object|exhibition|gallery))/(?P<document_id>[A-Za-z\d]+)$', views.manifest, name='manifest'),
    re_path(r'^(?P<document_type>(object|exhibition|gallery))/(?P<document_id>[A-Za-z\d]+)/list/(?P<canvas_id>[A-Za-z\d]+)$', views.list, name='list'),
    re_path(r'^delete/(?P<document_type>(object|exhibition|gallery))/(?P<document_id>[A-Za-z\d]+)$', views.delete, name='delete'),
    re_path(r'^refresh/(?P<document_type>(object|exhibition|gallery))/(?P<document_id>[A-Za-z\d]+)$', views.refresh, name='refresh'),
    re_path(r'^refresh/all/(?P<document_type>(object|exhibition|gallery))$', views.refresh_by_source, name='refresh_by_source'),
]
