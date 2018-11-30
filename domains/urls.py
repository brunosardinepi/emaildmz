from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'domains'

urlpatterns = [
    path('<str:alias_name>/create/', views.DomainCreate.as_view(), name='domain_create'),
    path('<int:pk>/delete/', views.DomainDelete.as_view(), name='domain_delete'),
]
