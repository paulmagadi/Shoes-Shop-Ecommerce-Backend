

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from cart.models import Cart, CartItem
from cart.views import get_or_create_cart
from mpesa.api import  send_stk_push
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from order.models import Order, OrderItem, ShippingAddress
from users.models import CustomUser

from django.contrib.auth.decorators import login_required
from django.db import transaction

# @login_required
# @require_POST
# @transaction.atomic
# def mpesa_checkout_view(request):
#     phone = request.POST.get("phone")
#     shipping_address_id = request.POST.get("shipping_address")

#     cart = get_or_create_cart(request)
#     items = CartItem.objects.filter(cart=cart)

#     if not items.exists():
#         return JsonResponse({"error": "Cart is empty."}, status=400)

#     shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id, user=request.user)

#     total = sum(item.get_total_price() for item in items)

    # # Initiate STK Push
    # callback_url = request.build_absolute_uri(reverse("mpesa_callback"))
    # response = initiate_stk_push(
    #     phone=phone,
    #     amount=int(total),
    #     account_reference=f"user_{request.user.id}",
    #     callback_url=callback_url,
    #     description="Shoes Order"
    # )

    # # Store temporary order in session (we’ll create it on callback success)
    # request.session["pending_order"] = {
    #     "shipping_address_id": shipping_address.id,
    #     "phone": phone,
    #     "total": float(total)
    # }

    # return JsonResponse(response)
    

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
        item.variant.stock -= item.quantity
        item.variant.save()

    cart.items.all().delete()

    # 🔁 Send STK push
    response = send_stk_push(phone, total, order.id)
    return JsonResponse(response)




@csrf_exempt
@transaction.atomic
def mpesa_callback(request):
    import json
    data = json.loads(request.body)

    result_code = data['Body']['stkCallback']['ResultCode']
    metadata = data['Body']['stkCallback'].get('CallbackMetadata')

    if result_code == 0:
        phone = next((i["Value"] for i in metadata["Item"] if i["Name"] == "PhoneNumber"), None)

        # Retrieve order data (in real apps, track by CheckoutRequestID)
        user = CustomUser.objects.filter(email="...")  # Add logic to find user by phone if needed

        # You can store more precise mapping in session/db
        pending_data = request.session.get("pending_order")
        if pending_data:
            address = ShippingAddress.objects.get(id=pending_data["shipping_address_id"])
            cart = Cart.objects.get(user=user)
            items = CartItem.objects.filter(cart=cart)

            # Create Order
            order = Order.objects.create(
                user=user,
                shipping_address=address,
                total_price=pending_data["total"],
                payment_method="mpesa",
                payment_status="paid"
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

            cart.items.all().delete()
            # Optionally clear session['pending_order']

    return JsonResponse({"ResultCode": 0, "ResultDesc": "OK"})


# mpesa/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def mpesa_thank_you(request):
    return render(request, 'mpesa/thank_you.html')
