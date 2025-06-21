# order/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('cod/', views.cod_checkout_view, name='cod_checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),
    path('address/add/', views.add_shipping_address, name='add_shipping_address'),
    path('address/edit/<int:pk>/', views.edit_shipping_address, name='edit_shipping_address'),
    path('address/delete/<int:pk>/', views.delete_shipping_address, name='delete_shipping_address'),
    path('address/select/', views.select_shipping_address, name='select_shipping_address'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation_view, name='order_confirmation'),


]

