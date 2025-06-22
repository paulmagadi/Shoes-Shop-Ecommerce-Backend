from django.db import models
from django.conf import settings
from order.models import Order, ShippingAddress

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("pending", "Pending"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    phone_number = models.CharField(max_length=15)
    mpesa_receipt_number = models.CharField(max_length=30, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="initiated")
    checkout_request_id = models.CharField(max_length=50, null=True, blank=True)
    response_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.ForeignKey(ShippingAddress, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transaction {self.mpesa_receipt_number or 'N/A'} - {self.status} - {self.phone_number}"
