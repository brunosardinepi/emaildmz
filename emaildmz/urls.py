from django.contrib import admin
from django.urls import include, path

from . import config
from . import views


urlpatterns = [
    path('{}/'.format(config.settings['admin']), admin.site.urls),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/signup/', views.SignupView.as_view(), name='signup'),
    path('accounts/', include('allauth.urls')),
#    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
#    path('dashboard/<str:alias_name>/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/<str:alias_name>/', views.dashboard_view, name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('aliases/', include('aliases.urls', namespace='aliases')),
    path('domains/', include('domains.urls', namespace='domains')),
    path('', views.HomeView.as_view(), name='home'),
]
