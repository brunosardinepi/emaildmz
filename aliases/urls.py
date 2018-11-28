from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'aliases'

urlpatterns = [
    path('', views.ForwardingEmailListView.as_view(), name='forwardingemail_list'),
]