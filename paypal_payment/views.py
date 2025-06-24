from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponseBadRequest

from paypal.standard.forms import PayPalPaymentsForm

from cart.views import get_or_create_cart
from cart.models import CartItem
from order.models import Order, OrderItem, ShippingAddress


@require_GET
@login_required
def start_paypal_payment(request, order_id):
    """
    Initiates the PayPal redirect after creating the order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    host = request.get_host()

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": order.total_price,
        "item_name": f"Order #{order.id}",
        "invoice": str(order.id),
        "currency_code": "USD",
        "notify_url": f"http://{host}{reverse('paypal-ipn')}",
        "return_url": f"http://{host}{reverse('paypal_success')}?order_id={order.id}",
        "cancel_return": f"http://{host}{reverse('paypal_cancel')}",
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "paypal_payment/pay.html", {"form": form})


@require_POST
@login_required
@transaction.atomic
def create_paypal_order(request):
    """
    Creates a pending order and redirects user to PayPal gateway.
    """
    shipping_address_id = request.POST.get("shipping_address")
    if not shipping_address_id:
        return HttpResponseBadRequest("Missing shipping address.")

    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, user=request.user)
    cart = get_or_create_cart(request)
    items = cart.items.select_related("variant__product_color__product", "variant__size")

    if not items.exists():
        return redirect("cart_detail")

    total = sum(item.get_total_price() for item in items)

    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        status="pending",
        payment_method="paypal",
        payment_status="unpaid",
        total_price=total,
    )

    return redirect("start_paypal_payment", order_id=order.id)


@login_required
@transaction.atomic
def paypal_success(request):
    """
    Finalizes the order after PayPal redirects back (non-IPN fallback).
    """
    order_id = request.GET.get("order_id")
    tx_id = request.GET.get("tx") or request.GET.get("txnid")

    if not order_id:
        return HttpResponseBadRequest("Missing order_id")

    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == "paid":
        return render(request, "paypal_payment/paypal_success.html", {"order": order})

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)

    for item in items:
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.variant.sale_price or item.variant.price
        )
        item.variant.stock -= item.quantity
        item.variant.save()

    cart.items.all().delete()

    order.payment_status = "paid"
    order.status = "processing"
    order.paid_at = timezone.now()
    if tx_id:
        order.transaction_id = tx_id
    order.save()

    return render(request, "paypal_payment/paypal_success.html", {"order": order})


def paypal_cancel(request):
    """
    Called when user cancels PayPal payment.
    """
    messages.warning(request, "Payment was cancelled.")
    return render(request, "paypal_payment/cancel.html")
