from django.urls import path
from . import views

urlpatterns = [
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('ajax/get-variants/<int:color_id>/', views.get_variants_by_color, name='get_variants_by_color'),

]