from django.urls import re_path

from viewers import views

urlpatterns = [
    re_path(r'^(?P<viewer_type>(mirador))/(?P<viewer_version>(v1|v2|v3))$', views.view, name='view'),
    re_path(r'^(?P<viewer_type>(mirador))$', views.view, name='view'),
]
