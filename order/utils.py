from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - #{order.id}"
    to_email = order.user.email
    from_email = settings.DEFAULT_FROM_EMAIL

    context = {"order": order}
    message = render_to_string("order/email/order_receipt.html", context)

    send_mail(subject, message, from_email, [to_email], fail_silently=False)
