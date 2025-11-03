from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'sysadmin'


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('login/', auth_views.LoginView.as_view(template_name='sysadmin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('availability/', views.availability, name='availability'),
    path('availability/toggle/', views.toggle_availability, name='toggle_availability'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('appointments/<int:appointment_id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('api/available-slots/', views.get_available_slots_for_date, name='get_available_slots'),
    path('analytics/', views.analytics, name='analytics'),
    path('reports/', views.reports, name='reports'),
    path('reports/export-pdf/', views.export_report_pdf, name='export_report_pdf'),
    path('profile-picture/<int:user_id>/', views.profile_picture, name='profile_picture'),
    path('profile/', views.profile, name='profile'),
]


