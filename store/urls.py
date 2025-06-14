from django.urls import path
from . import views

urlpatterns = [
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
]