import json
from datetime import timezone

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

from cart.models import CartItem
from cart.views import get_or_create_cart
from mpesa.api import send_stk_push
from order.models import Order, OrderItem, ShippingAddress
from users.models import CustomUser


from mpesa.models import Transaction  
from mpesa.models import Transaction

@login_required
@require_POST
@transaction.atomic
def mpesa_checkout_view(request):
    phone = request.POST.get('phone')
    shipping_address_id = request.POST.get('shipping_address')

    if not phone or not shipping_address_id:
        return JsonResponse({'error': 'Missing phone or address'}, status=400)

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)
    if not items.exists():
        return JsonResponse({'error': 'Empty cart'}, status=400)

    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, user=request.user)
    total = sum(item.get_total_price() for item in items)

    # ✅ Create the Order in pending mode
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        status="pending",
        payment_method="mpesa",
        payment_status="pending",
        total_price=total
    )

    for item in items:
        if item.quantity > item.variant.stock:
            return JsonResponse({'error': f"Stock issue for {item.variant}"}, status=400)

        OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=item.quantity,
            price=item.variant.sale_price or item.variant.price
        )

        transaction = Transaction.objects.create(
            user=request.user,
            order=order,
            phone_number=phone,
            amount=total,
            status="initiated",
            checkout_request_id=response.get("CheckoutRequestID"),
            response_description=response.get("ResponseDescription")
        )

        item.variant.stock -= item.quantity
        item.variant.save()

    cart.items.all().delete()

    # 🔁 Initiate STK Push
    response = send_stk_push(phone, total, order.id)
    return JsonResponse(response)


@csrf_exempt
@transaction.atomic
def mpesa_payment_callback(request):
    try:
        data = json.loads(request.body)
        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        metadata = callback.get("CallbackMetadata", {}).get("Item", [])

        phone = next((item["Value"] for item in metadata if item["Name"] == "PhoneNumber"), None)
        receipt = next((item["Value"] for item in metadata if item["Name"] == "MpesaReceiptNumber"), None)
        amount = next((item["Value"] for item in metadata if item["Name"] == "Amount"), None)

        # if result_code == 0 and phone:
        #     order = Order.objects.filter(payment_status="pending", user__phone=phone).latest("created_at")
        #     order.payment_status = "paid"
        #     order.status = "processing"
        #     order.paid_at = timezone.now()
        #     order.save()
            

        # After processing the successful callback:
        if result_code == 0 and phone:
            order = Order.objects.filter(payment_status="pending", user__phone=phone).latest("created_at")
            order.payment_status = "paid"
            order.status = "processing"
            order.paid_at = timezone.now()
            order.save()

            # ✅ Update transaction
            Transaction.objects.filter(
                order=order, phone_number=phone, status="initiated"
            ).update(
                status="success",
                mpesa_receipt_number=mpesa_receipt,
            )
        else:
            # Log as failed
            Transaction.objects.filter(
                phone_number=phone, status="initiated"
            ).update(status="failed")


    except Exception as e:
        print("⚠️ MPesa callback error:", e)

    return JsonResponse({"ResultCode": 0, "ResultDesc": "Confirmation received successfully"})


@login_required
def mpesa_thank_you(request):
    return render(request, 'mpesa/thank_you.html')


@login_required
def order_confirmation_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order/confirmation.html", {"order": order})
