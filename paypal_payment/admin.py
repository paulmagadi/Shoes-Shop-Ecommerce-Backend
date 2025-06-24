# paypal_payment/admin.py
from django.contrib import admin
from .models import PayPalTransaction

@admin.register(PayPalTransaction)
class PayPalTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'created_at', 'confirmed_at')
    search_fields = ('transaction_id', 'user__email')
    list_filter = ('status', 'created_at')
