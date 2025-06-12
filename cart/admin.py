from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("variant", "quantity", "get_unit_price", "get_total_price")

    def get_unit_price(self, obj):
        return obj.get_unit_price()
    get_unit_price.short_description = "Unit Price"

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_id", "created_at", "updated_at", "total_items", "total_price")
    list_filter = ("user", "created_at")
    search_fields = ("user__username", "session_id")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "variant", "quantity", "get_unit_price", "get_total_price", "added_at")
    readonly_fields = ("added_at",)

    def get_unit_price(self, obj):
        return obj.get_unit_price()
    get_unit_price.short_description = "Unit Price"

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Total Price"
