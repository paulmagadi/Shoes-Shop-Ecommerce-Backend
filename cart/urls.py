from django.urls import path
from .views import cart_detail, add_to_cart, update_cart_item, remove_cart_item

urlpatterns = [
    path('cart/', cart_detail, name='cart_detail'),
    path('add/<int:variant_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('remove/<int:item_id>/', remove_cart_item, name='remove_cart_item'),
]
