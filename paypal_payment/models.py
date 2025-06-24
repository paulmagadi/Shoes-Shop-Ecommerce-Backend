from django.db import models
from django.conf import settings
from order.models import Order

class PayPalTransaction(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='paypal_transaction')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')  # pending, completed, failed
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "PayPal Transaction"

    def __str__(self):
        return f"PayPalTxn: {self.transaction_id} ({self.status})"
