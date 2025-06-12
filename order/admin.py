from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("variant", "quantity", "unit_price", "get_total_price")

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "payment_status", "total_price", "created_at", "paid_at")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("user__username", "id")
    readonly_fields = ("created_at", "paid_at", "total_price")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "variant", "quantity", "unit_price", "get_total_price")

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "country", "is_primary")
    search_fields = ("user__username", "full_name", "city", "country")
