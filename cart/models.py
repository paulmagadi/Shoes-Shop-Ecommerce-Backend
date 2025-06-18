from django.db import models
from store.models import Variant
from django.utils import timezone
import uuid
from users.models import CustomUser

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart ({self.user or self.session_id})"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('cart', 'variant')

    def get_unit_price(self):
        return self.variant.sale_price or self.variant.price

    def get_total_price(self):
        return self.get_unit_price() * self.quantity

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

