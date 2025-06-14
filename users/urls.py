from django.urls import path
from . import views


urlpatterns = [
    # User registration flow
    path('register/', views.register_user, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate'),
    path('resend-activation/', views.resend_activation_user, name='resend_activation'),
    
    # User login and logout
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]

from django.contrib.auth import views as auth_views

urlpatterns += [
    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Password change flow
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change.html'
    ), name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),
]

from .views import dashboard_view, update_profile_view

urlpatterns += [
    path('account/', dashboard_view, name='dashboard'),
    path('account/edit/', update_profile_view, name='edit_profile'),
]
