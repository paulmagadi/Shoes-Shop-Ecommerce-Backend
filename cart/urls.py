from django.urls import path
from .views import add_to_cart
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:variant_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('ajax/cart-count/', views.cart_count_view, name='cart_count'),
]
