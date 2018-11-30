from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'recipients'

urlpatterns = [
    path('<str:alias_name>/create/',
        views.RecipientCreate.as_view(),
        name='recipient_create'),
    path('<int:pk>/delete/',
        views.RecipientDelete.as_view(),
        name='recipient_delete'),
]
