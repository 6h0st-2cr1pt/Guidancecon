from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'sysadmin'


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='sysadmin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('availability/', views.availability, name='availability'),
    path('availability/toggle/', views.toggle_availability, name='toggle_availability'),
]


