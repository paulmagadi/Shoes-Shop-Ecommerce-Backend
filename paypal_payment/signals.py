from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
from order.models import Order
from mpesa.models import Transaction  # or adjust to your actual transaction/payment model
from django.utils.timezone import now

@receiver(valid_ipn_received)
def paypal_payment_complete(sender, **kwargs):
    ipn = sender

    if ipn.payment_status == "Completed":
        try:
            # Match order using invoice
            order_id = int(ipn.invoice.split("-")[-1])
            order = Order.objects.get(id=order_id, payment_method="paypal", payment_status="unpaid")

            # Mark as paid
            order.payment_status = "paid"
            order.status = "processing"
            order.paid_at = now()
            order.save()

            # Optionally log transaction
            Transaction.objects.create(
                user=order.user,
                order=order,
                amount=ipn.mc_gross,
                status="success",
                mpesa_receipt_number=ipn.txn_id,  # reuse field if needed
                phone_number=ipn.payer_email
            )

        except Order.DoesNotExist:
            # Could not find a matching unpaid order
            pass
