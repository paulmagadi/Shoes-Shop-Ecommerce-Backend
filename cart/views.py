from django.shortcuts import render, redirect, get_object_or_404
from store.models import Variant
from .models import Cart, CartItem
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from cart import models

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
    quantity = int(request.POST.get('quantity', 1))

    if quantity > variant.stock:
        message = "Not enough stock available."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'status': 'error', 'message': message}, status=400)
        messages.warning(request, message)
        return redirect('product_detail', slug=variant.product_color.product.slug)

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

    if cart_item.quantity + quantity > variant.stock:
        message = "You've exceeded the available stock."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'status': 'error', 'message': message}, status=400)
        messages.warning(request, message)
    else:
        cart_item.quantity += quantity
        cart_item.save()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'status': 'success', 'message': "Item added to cart."})
        messages.success(request, "Item added to cart.")
    
    return redirect('cart_detail')



@transaction.atomic
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > cart_item.variant.stock:
        messages.warning(request, "Not enough stock.")
    elif quantity < 1:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart_detail')


@transaction.atomic
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    messages.success(request, "Item removed.")
    return redirect('cart_detail')


def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('variant__product_color', 'variant__size')
    total = sum([item.get_total_price() for item in items]) if items else 0
    return render(request, 'cart/cart_detail.html', {'items': items, 'total': total})



from django.http import JsonResponse
from .models import Cart

def cart_count_view(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            session_id = request.session.session_key or request.session.save()
            cart = Cart.objects.get(session_id=session_id)

        count = cart.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    except Cart.DoesNotExist:
        pass

    return JsonResponse({'cart_count': count})
