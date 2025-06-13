from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate'),
    path('resend-activation/', views.resend_activation_user, name='resend_activation'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]

