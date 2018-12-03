from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views


app_name = 'filters'

urlpatterns = [
    path('<str:alias_name>/create/', views.FilterCreate.as_view(), name='filter_create'),
    path('<int:pk>/delete/', views.FilterDelete.as_view(), name='filter_delete'),
    path('<int:pk>/filter/<str:action>/',
        views.FilterFilter.as_view(),
        name='filter_filter'),
]
