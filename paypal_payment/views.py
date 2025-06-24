from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from paypal.standard.forms import PayPalPaymentsForm

from cart.models import CartItem
from cart.views import get_or_create_cart
from order.models import Order, OrderItem, ShippingAddress
from paypal_payment.models import PayPalTransaction


# 🔁 Prepare and display PayPal payment form
@login_required
@transaction.atomic
@csrf_exempt  # CSRF exempt to allow POST redirect from frontend
def start_paypal_payment(request):
    if request.method != "POST":
        return redirect("checkout")

    shipping_address_id = request.POST.get("shipping_address")
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, user=request.user)

    cart = get_or_create_cart(request)
    items = cart.items.select_related("variant__product_color__product", "variant__size")
    if not items.exists():
        return redirect("cart_detail")

    total = sum(item.get_total_price() for item in items)
    invoice_id = f"{request.user.id}-{int(timezone.now().timestamp())}"

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": total,
        "item_name": f"Order for {request.user.email}",
        "invoice": invoice_id,
        "currency_code": "USD",
        "notify_url": f"https://a989-102-0-21-194.ngrok-free.app{reverse('paypal-ipn')}",
        "return": request.build_absolute_uri(reverse('paypal_success')),
        "cancel_return": request.build_absolute_uri(reverse('paypal_cancel')),
        "rm": "2",  # POST return method for PayPal
        "custom": str(request.user.id),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)

    return render(request, "paypal_payment/pay.html", {
        "form": form,
        "cart_items": items,
        "total": total,
    })


# ✅ Handle successful PayPal payment return (fallback if IPN fails)
@login_required
@transaction.atomic
@csrf_exempt  # CSRF exempt to allow POST redirect from frontend

def paypal_success(request):
    tx_id = request.GET.get("tx") or request.GET.get("txnid")
    if not tx_id:
        return redirect("checkout")

    # Prevent duplicate order creation
    existing = Order.objects.filter(transaction_id=tx_id, user=request.user).first()
    if existing:
        return render(request, "paypal_payment/paypal_success.html", {"order": existing})

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)
    if not items.exists():
        return redirect("cart_detail")

    shipping_address = ShippingAddress.objects.filter(user=request.user, is_primary=True).first()
    if not shipping_address:
        return redirect("checkout")

    total = sum(item.get_total_price() for item in items)

    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_price=total,
        status="processing",
        payment_method="paypal",
        payment_status="paid",
        transaction_id=tx_id,
        paid_at=timezone.now(),
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.variant.sale_price or item.variant.price,
        )
        item.variant.stock -= item.quantity
        item.variant.save()

    PayPalTransaction.objects.get_or_create(
        order=order,
        user=request.user,
        transaction_id=tx_id,
        defaults={
            'amount': order.total_price,
            'status': 'completed',
            'confirmed_at': timezone.now()
        }
    )

    cart.items.all().delete()
    send_order_confirmation_email(request.user, order)

    return render(request, "paypal_payment/paypal_success.html", {"order": order})


# ❌ Handle cancellation
def paypal_cancel(request):
    messages.warning(request, "Payment was cancelled.")
    return render(request, "paypal_payment/cancel.html")


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(user, order):
    subject = f"Order Confirmation - #{order.id}"
    message = render_to_string("emails/order_confirmation_email.txt", {
        "user": user,
        "order": order,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
