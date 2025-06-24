# from django.urls import path
# from . import views

# urlpatterns = [
#     path('start/<int:order_id>/', views.start_paypal_payment, name='start_paypal_payment'),
#     path('return/', views.paypal_return, name='paypal_return'),
#     path('cancel/', views.paypal_cancel, name='paypal_cancel'),
#     path('success/', views.paypal_success, name='paypal_success'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path("start/<int:order_id>/", views.start_paypal_payment, name="start_paypal_payment"),
    path("success/", views.paypal_success, name="paypal_success"),
    path("cancel/", views.paypal_cancel, name="paypal_cancel"),
    path("checkout/paypal/", views.create_paypal_order, name="create_paypal_order"),

]
