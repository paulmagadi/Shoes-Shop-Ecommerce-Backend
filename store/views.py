from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductColor, Variant, ProductImage

def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    colors = product.colors.select_related('color').prefetch_related('images', 'variants__size')
    
    # Featured color instead of .first
    selected_color = product.colors.filter(is_featured=True).first() or colors.first()
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
    
    
from django.http import JsonResponse
from .models import ProductColor

def get_product_color_details(request, color_id):
    try:
        color = ProductColor.objects.prefetch_related('images', 'variants__size').get(id=color_id)

        images = [img.image.url for img in color.images.all()]
        variants = [{
            'id': v.id,
            'size': str(v.size),
            'price': str(v.price),
            'sale_price': str(v.sale_price) if v.sale_price else None,
            'stock': v.stock
        } for v in color.variants.all()]


        return JsonResponse({
            'images': images,
            'variants': variants
        })

    except ProductColor.DoesNotExist:
        return JsonResponse({'error': 'Color not found'}, status=404)


