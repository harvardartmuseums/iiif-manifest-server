from django.conf.urls import patterns, url

from viewers import views

urlpatterns = patterns('',
    url(r'^(?P<viewer_type>(mirador))$', views.view, name='view'),
)
