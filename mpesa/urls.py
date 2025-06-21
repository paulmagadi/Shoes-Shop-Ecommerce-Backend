from django.urls import path
from . import views

urlpatterns = [
    path("mpesa/", views.mpesa_checkout_view, name="mpesa_checkout"),
    path("mpesa/callback/", views.mpesa_callback, name="mpesa_callback"),
    path('thank-you/', views.mpesa_thank_you, name='mpesa_thank_you'),
]