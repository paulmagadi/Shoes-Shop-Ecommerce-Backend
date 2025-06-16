from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductColor, Variant, ProductImage

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    colors = product.colors.select_related('color').prefetch_related('variants', 'images')

    selected_color = colors.first()  # default selection
    selected_variants = selected_color.variants.select_related('size') if selected_color else []

    return render(request, 'store/product_detail.html', {
        'product': product,
        'colors': colors,
        'selected_color': selected_color,
        'variants': selected_variants,
    })
    
    
from django.http import JsonResponse
from .models import ProductColor

def get_variants_by_color(request, color_id):
    try:
        product_color = ProductColor.objects.prefetch_related('variants__size').get(id=color_id)
        variants = product_color.variants.all()
        data = [
            {
                'id': variant.id,
                'size': str(variant.size),
                'stock': variant.stock,
                'price': str(variant.price),
            } for variant in variants
        ]
        return JsonResponse({'variants': data})
    except ProductColor.DoesNotExist:
        return JsonResponse({'error': 'Color not found'}, status=404)

