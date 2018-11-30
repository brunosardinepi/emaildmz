from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'aliases'

urlpatterns = [
    path('create/', views.AliasCreate.as_view(), name='alias_create'),
    path('delete/<str:name>/', views.AliasDelete.as_view(), name='alias_delete'),

    path('<str:alias_name>/forwardingemail/create/',
        views.ForwardingEmailCreate.as_view(),
        name='forwardingemail_create'),
    path('<str:alias_name>/forwardingemail/<int:pk>/delete/',
        views.ForwardingEmailDelete.as_view(),
        name='forwardingemail_delete'),
]
