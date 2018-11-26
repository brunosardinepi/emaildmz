from django.contrib import admin
from django.urls import include, path

from . import config


urlpatterns = [
    path('{}/'.format(config.settings['admin']), admin.site.urls),
    path('accounts/', include('allauth.urls')),
]
