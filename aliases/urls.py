from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'aliases'

urlpatterns = [
    path('create/', views.AliasCreate.as_view(), name='alias_create'),
]
