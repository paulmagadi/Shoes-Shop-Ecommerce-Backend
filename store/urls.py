from django.urls import path
from . import views
from . import search_views

urlpatterns = [
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('ajax/get-variants/<int:color_id>/', views.get_variants_by_color, name='get_variants_by_color'),
    path('ajax/product-color/<int:color_id>/', views.get_product_color_details, name='get_product_color_details'),

    path("search/", search_views.product_search_view, name="product_search"),
    # path("search/suggest/", search_views.search_suggest_view, name="search_suggest"),
    # path("search/filters/", search_views.search_filters_view, name="search_filters"),
    path('products/', views.product_list_view, name='product_list'),

]