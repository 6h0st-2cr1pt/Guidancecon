from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('appointments/', views.appointments, name='appointments'),
    path('counselor/<int:counselor_id>/availability/', views.counselor_availability, name='counselor_availability'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('notifications/', views.notifications, name='notifications'),
    path('profile-picture/<int:user_id>/', views.profile_picture, name='profile_picture'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='public:home'), name='logout'),
]


