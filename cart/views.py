from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Cart, CartItem
from store.models import Variant
from . import models

# -----------------------
# Cart Helper
# -----------------------
# def get_or_create_cart(request):
#     if request.user.is_authenticated:
#         cart, _ = Cart.objects.get_or_create(user=request.user)
#     else:
#         session_id = request.session.session_key or request.session.save()
#         cart, _ = Cart.objects.get_or_create(session_id=session_id)
#     return cart

# # -----------------------
# # Add to Cart
# # -----------------------
# from django.http import JsonResponse, HttpResponseBadRequest

# @transaction.atomic
# def add_to_cart(request, variant_id):
#     try:
#         variant = get_object_or_404(Variant, id=variant_id)
#         quantity = int(request.POST.get('quantity', 1))

#         if quantity < 1 or quantity > variant.stock:
#             if request.headers.get("x-requested-with") == "XMLHttpRequest":
#                 return JsonResponse({"success": False, "error": "Invalid quantity"}, status=400)
#             raise ValueError("Invalid quantity")

#         cart = get_or_create_cart(request)
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

#         if cart_item.quantity + quantity > variant.stock:
#             if request.headers.get("x-requested-with") == "XMLHttpRequest":
#                 return JsonResponse({"success": False, "error": "Stock exceeded"}, status=400)
#             raise ValueError("Stock exceeded")

#         cart_item.quantity += quantity
#         cart_item.save()

#         if request.headers.get("x-requested-with") == "XMLHttpRequest":
#             count = cart.items.aggregate(total=models.models.Sum('quantity'))['total'] or 0
#             return JsonResponse({"success": True, "cart_count": count})

#         return redirect('cart_detail')

#     except Exception as e:
#         if request.headers.get("x-requested-with") == "XMLHttpRequest":
#             return JsonResponse({"success": False, "error": str(e)}, status=500)
#         raise  # Let Django render the default error page if not AJAX


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from .models import Cart, CartItem
from store.models import Variant
from django.db.models import Sum


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key or request.session.save()
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


@transaction.atomic
def add_to_cart(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)
        messages.error(request, "Invalid quantity")
        return redirect('product_detail', slug=variant.product_color.product.slug)

    if quantity < 1:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': False, 'error': 'Quantity must be at least 1'}, status=400)
        messages.warning(request, "Quantity must be at least 1")
        return redirect('product_detail', slug=variant.product_color.product.slug)

    if quantity > variant.stock:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': False, 'error': 'Not enough stock available'}, status=400)
        messages.warning(request, "Not enough stock available.")
        return redirect('product_detail', slug=variant.product_color.product.slug)

    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={'quantity': quantity}
    )

    if not created:
        if cart_item.quantity + quantity > variant.stock:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({'success': False, 'error': 'You’ve exceeded the available stock'}, status=400)
            messages.warning(request, "You've exceeded the available stock.")
            return redirect('product_detail', slug=variant.product_color.product.slug)

        cart_item.quantity += quantity
        cart_item.save()

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total_items = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'success': True, 'cart_count': total_items})

    messages.success(request, "Item added to cart.")
    return redirect('cart_detail')



# -----------------------
# Cart Detail View
# -----------------------
def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related(
        'variant__product_color__product',
        'variant__product_color__color',
        'variant__size'
    )
    total = sum(item.get_total_price() for item in items)
    return render(request, 'cart/cart_detail.html', {'items': items, 'total': total})


# -----------------------
# Update Cart Item (AJAX)
# -----------------------
@require_POST
@transaction.atomic
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        qty = int(request.POST.get("quantity"))
        if qty < 1 or qty > item.variant.stock:
            return HttpResponseBadRequest("Invalid quantity")
        item.quantity = qty
        item.save()
        return JsonResponse({
            "success": True,
            "item_total": item.get_total_price(),
            "variant_id": item.variant.id
        })
    except:
        return HttpResponseBadRequest("Error")

# -----------------------
# Remove Cart Item (AJAX)
# -----------------------
@require_POST
@transaction.atomic
def remove_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return JsonResponse({"success": True})

# -----------------------
# Cart Count View (for navbar icon)
# -----------------------
def cart_count_view(request):
    count = 0
    try:
        cart = Cart.objects.get(user=request.user) if request.user.is_authenticated else \
               Cart.objects.get(session_id=request.session.session_key or request.session.save())
        count = cart.items.aggregate(total=models.models.Sum('quantity'))['total'] or 0
    except Cart.DoesNotExist:
        pass

    return JsonResponse({'cart_count': count})
