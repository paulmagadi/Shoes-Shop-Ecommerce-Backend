from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductImage, Variant

# Create your views here.
def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.select_related('color').prefetch_related('images')
    return render(request, 'store/product_detail.html', {
        'product': product,
        'variants': variants,
    })
