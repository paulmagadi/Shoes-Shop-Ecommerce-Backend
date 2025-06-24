import json
from django.utils import timezone

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction

from cart.models import CartItem
from cart.views import get_or_create_cart
from mpesa.api import send_stk_push
from mpesa.models import Transaction
from order.models import Order, OrderItem, ShippingAddress


# 🔁 Initiate MPesa Payment (STK Push Only)
@login_required
@require_POST
@transaction.atomic
def initiate_mpesa_payment(request):
    phone = request.POST.get('phone')
    shipping_address_id = request.POST.get('shipping_address')

    if not phone or not shipping_address_id:
        return JsonResponse({'error': 'Missing phone or address'}, status=400)

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)
    if not items.exists():
        return JsonResponse({'error': 'Empty cart'}, status=400)

    total = sum(item.get_total_price() for item in items)

    # Send STK Push
    response = send_stk_push(phone, total)
    if response.get("ResponseCode") != "0":
        return JsonResponse({'error': 'Failed to initiate STK'}, status=500)

    # Log transaction only (no order yet)
    txt = Transaction.objects.create(
        user=request.user,
        phone_number=phone,
        amount=total,
        status="pending",
        checkout_request_id=response.get("CheckoutRequestID"),
        shipping_address_id=shipping_address_id
    )

    

    return JsonResponse({
        'success': True,
        'message': 'STK Push sent',
        'transaction_id': txt.id
    })


# 🔄 Poll payment status from frontend
@login_required
def poll_payment_status(request, transaction_id):
    txn = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    return JsonResponse({'status': txn.status})


# ✅ Create Order after confirmed payment
@login_required
@transaction.atomic
def complete_mpesa_order(request, transaction_id):
    txn = get_object_or_404(Transaction, id=transaction_id, user=request.user, status="success")

    if txn.order:
        return JsonResponse({'redirect_url': reverse('order_confirmation', args=[txn.order.id])})

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)

    order = Order.objects.create(
        user=request.user,
        shipping_address_id=txn.shipping_address_id,
        total_price=txn.amount,
        status="processing",
        payment_method="mpesa",
        payment_status="paid",
        paid_at=timezone.now()
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.variant.sale_price or item.variant.price
        )
        item.variant.stock -= item.quantity
        item.variant.save()

    txn.order = order
    txn.save()
    cart.items.all().delete()
    
    
    # ✉️ Send confirmation email
    send_order_confirmation_email(order)

    return JsonResponse({'redirect_url': reverse('order_confirmation', args=[order.id])})



# 📥 Handle MPesa STK Push Callback
@csrf_exempt
@transaction.atomic
def mpesa_callback(request):
    try:
        data = json.loads(request.body)
        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        metadata = callback.get("CallbackMetadata", {}).get("Item", [])
        checkout_id = callback["CheckoutRequestID"]

        phone = next((i["Value"] for i in metadata if i["Name"] == "PhoneNumber"), None)
        receipt = next((i["Value"] for i in metadata if i["Name"] == "MpesaReceiptNumber"), None)

        txn = Transaction.objects.get(checkout_request_id=checkout_id)

        if result_code == 0:
            txn.status = "success"
            txn.mpesa_receipt_number = receipt
        else:
            txn.status = "failed"

        txn.save()

    except Exception as e:
        print("⚠️ MPesa Callback Error:", e)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Processed"})


# 🎉 Simple Thank You page (optional)
@login_required
def mpesa_thank_you(request):
    return render(request, 'mpesa/thank_you.html')


# ✅ Final Order Confirmation View
@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order/confirmation.html", {"order": order})


# utils/email.py or directly in views.py for now
from django.core.mail import send_mail
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f"Order #{order.id} Confirmation"
    message = (
        f"Hi {order.user.first_name},\n\n"
        f"Your order #{order.id} has been received and is being processed.\n"
        f"Total Amount: KES {order.total_price}\n"
        f"Shipping to: {order.shipping_address.full_name}, {order.shipping_address.city}\n\n"
        "We'll notify you when it's shipped.\n\nThank you for shopping with us!"
    )
    recipient = order.user.email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])



# utils/email.py
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.conf import settings

# def send_order_confirmation_email(order):
#     subject = f"✅ Order #{order.id} Confirmation - {settings.SITE_NAME}"
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = [order.user.email]

#     context = {
#         "order": order,
#         "user": order.user,
#         "items": order.items.all(),
#         "shipping": order.shipping_address,
#     }

#     # Render both plain and HTML versions
#     text_body = render_to_string("emails/order_confirmation.txt", context)
#     html_body = render_to_string("emails/order_confirmation.html", context)

#     email = EmailMultiAlternatives(subject, text_body, from_email, to_email)
#     email.attach_alternative(html_body, "text/html")
#     email.send()


# import africastalking

# def send_sms_confirmation(phone, order):
#     africastalking.initialize(username="your_username", api_key="your_api_key")
#     sms = africastalking.SMS
#     message = f"Hi {order.user.first_name}, your order #{order.id} for KES {order.total_price} is confirmed. Thanks!"
#     sms.send(message, [phone])



#     send_sms_confirmation(txn.phone_number, order)
