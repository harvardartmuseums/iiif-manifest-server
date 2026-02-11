from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    path('collections/', include('collections_iiif.urls')),
    path('manifests/', include('manifests.urls')),
    path('viewers/', include('viewers.urls')),
    path('admin/', admin.site.urls),
]
