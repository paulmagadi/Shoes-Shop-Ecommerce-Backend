from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.utils import timezone
from order.models import Order, OrderItem, ShippingAddress
from cart.models import CartItem
from cart.views import get_or_create_cart
from users.models import CustomUser

from cart.models import Cart
from paypal_payment.models import PayPalTransaction  # Import your model


@receiver(valid_ipn_received)
def paypal_payment_completed(sender, **kwargs):
    ipn_obj = sender

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            user_id = int(ipn_obj.custom)
            from users.models import CustomUser
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            print("⚠️ IPN Error: Invalid user ID", e)
            return

        # Check if order already exists
        if not Order.objects.filter(transaction_id=ipn_obj.txn_id).exists():
            cart = Cart.objects.filter(user=user).first()
            if not cart or not CartItem.objects.filter(cart=cart).exists():
                return
            items = CartItem.objects.filter(cart=cart)
            if not items.exists():
                return

            address = ShippingAddress.objects.filter(user=user, is_primary=True).first()
            if not address:
                return

            total = sum(item.get_total_price() for item in items)

            # ✅ Create Order
            order = Order.objects.create(
                user=user,
                shipping_address=address,
                total_price=total,
                status="processing",
                payment_method="paypal",
                payment_status="paid",
                transaction_id=ipn_obj.txn_id,
                paid_at=timezone.now()
            )

            # ✅ Create OrderItems
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

            # ✅ Log Transaction
            PayPalTransaction.objects.create(
                order=order,
                user=user,
                transaction_id=ipn_obj.txn_id,
                amount=ipn_obj.mc_gross,
                status="completed",
                confirmed_at=timezone.now()
            )
