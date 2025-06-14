from django.shortcuts import render, redirect, get_object_or_404
from store.models import Variant
from .models import Cart, CartItem
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
        messages.warning(request, "Not enough stock available.")
        return redirect('product_detail', slug=variant.product.slug)

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

    # Safe update
    if cart_item.quantity + quantity > variant.stock:
        messages.warning(request, "You've exceeded the available stock.")
    else:
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, "Item added to cart.")
    
    return redirect('cart_detail')


@transaction.atomic
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user if request.user.is_authenticated else None)
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
    items = cart.items.select_related('variant__product', 'variant__color', 'variant__size')
    total = sum([item.get_total_price() for item in items])
    return render(request, 'cart/cart_detail.html', {'items': items, 'total': total})
