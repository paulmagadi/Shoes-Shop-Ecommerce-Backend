from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_paypal_payment, name="start_paypal_payment"),
    path("success/", views.paypal_success, name="paypal_success"),
    path("cancel/", views.paypal_cancel, name="paypal_cancel"),

]
