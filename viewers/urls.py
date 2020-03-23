from django.conf.urls import patterns, url

from viewers import views

urlpatterns = patterns('',
    url(r'^(?P<viewer_type>(mirador))/(?P<viewer_version>(v1|v2|v3))$', views.view, name='view'),
    url(r'^(?P<viewer_type>(mirador))$', views.view, name='view'),
)
