from django.db import models
from django.conf import settings
from store.models import Variant
from django.utils import timezone


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    alternative_address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Shipping Addresses"
    
    def save(self, *args, **kwargs):
        if self.primary:
            ShippingAddress.objects.filter(user=self.user, primary=True).update(primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name}, {self.city} ({'Primary' if self.primary else 'Secondary'})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=50, default="stripe")  # or "cod", "paypal", etc.
    payment_status = models.CharField(max_length=50, default="unpaid")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.unit_price * self.quantity 

    def __str__(self):
        return f"{self.variant} x {self.quantity}"
