# order/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order
from cart.views import get_or_create_cart
from cart.models import CartItem
from .models import ShippingAddress
from django.contrib.auth.decorators import login_required
from django.db import transaction

@login_required
@transaction.atomic
def checkout_view(request):
    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)

    if request.method == "POST":
        shipping_address_id = request.POST.get('shipping_address')
        shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, user=request.user)

        # 🧾 Create Order
        order = Order.objects.create(user=request.user, shipping_address=shipping_address)

        for item in items:
            order.items.create(
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.sale_price or item.variant.price
            )
            item.variant.stock -= item.quantity
            item.variant.save()

        # ✅ Clear Cart
        cart.items.all().delete()

        return redirect('order_confirmation', order_id=order.id)

    # GET
    shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in items)
    return render(request, 'order/checkout.html', {
        'items': items,
        'shipping_addresses': shipping_addresses,
        'total': total,
    })


@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order/confirmation.html', {'order': order})


# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ShippingAddress
from .forms import ShippingAddressForm

@login_required
def add_shipping_address(request):
    form = ShippingAddressForm(request.POST or None)
    next_url = request.GET.get('next', 'checkout')  # fallback to checkout if no next provided

    if request.method == 'POST':
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user = request.user
            shipping.save()
            return redirect(next_url)

    return render(request, 'order/shipping_address_form.html', {
        'form': form,
        'title': 'Add Shipping Address',
    })


@login_required
def edit_shipping_address(request, pk):
    address = get_object_or_404(ShippingAddress, id=pk, user=request.user)
    form = ShippingAddressForm(request.POST or None, instance=address)
    next_url = request.GET.get('next', 'checkout')

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(next_url)

    return render(request, 'orders/shipping_address_form.html', {
        'form': form,
        'title': 'Edit Shipping Address',
    })

# orders/views.py
from django.contrib import messages

@login_required
def delete_shipping_address(request, pk):
    address = get_object_or_404(ShippingAddress, id=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Shipping address deleted.")
        return redirect(request.GET.get('next', 'checkout'))
    return render(request, 'orders/confirm_delete.html', {'address': address})


@login_required
@transaction.atomic
def select_shipping_address(request):
    if request.method == 'POST':
        selected_id = request.POST.get('selected_address')
        if selected_id:
            ShippingAddress.objects.filter(user=request.user, is_primary=True).update(is_primary=False)
            ShippingAddress.objects.filter(id=selected_id, user=request.user).update(is_primary=True)
            messages.success(request, "Shipping address selected.")
    return redirect('checkout')

