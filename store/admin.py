from django.contrib import admin
from .models import (
    Category, Brand, Type, Gender, Material, Color, Size,
    Product, Variant, ProductImage
)
from django.utils.html import format_html
from django.utils.timezone import now

from django.utils import timezone

from mptt.admin import DraggableMPTTAdmin



# -----------------------------
# Admin Actions
# -----------------------------
@admin.action(description="Archive selected products")
def archive_products(modeladmin, request, queryset):
    for product in queryset:
        product.archive()

@admin.action(description="Unarchive selected products")
def unarchive_products(modeladmin, request, queryset):
    for product in queryset:
        product.unarchive()

@admin.action(description="Permanently delete archived products")
def permanently_delete_products(modeladmin, request, queryset):
    queryset.filter(is_archived=True).delete()


# -----------------------------
# Inlines
# -----------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'is_featured')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    show_change_link = True


# -----------------------------
# Product Admin
# -----------------------------
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ("name", "brand", "category", "is_active", "is_archived", "created_at")
#     list_filter = ("is_active", "is_archived", "brand", "category", "gender")
#     search_fields = ("name", "brand__name", "category__name")
#     inlines = [VariantInline]
#     actions = [archive_products, unarchive_products, permanently_delete_products]
#     prepopulated_fields = {"slug": ("name",)}
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "is_active", "is_archived", "approved_by", "approved_at", "created_at")
    list_filter = ("is_active", "is_archived", "brand", "category")
    readonly_fields = ("approved_by", "approved_at")
    search_fields = ("name", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    actions = ['approve_selected_products']

    def approve_selected_products(self, request, queryset):
        if not request.user.has_perm("yourapp.can_approve_product"):
            self.message_user(request, "You don't have permission to approve products.", level='error')
            return

        updated_count = queryset.update(
            is_active=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f"{updated_count} product(s) approved and listed.")

    approve_selected_products.short_description = "✅ Approve and list selected products"

    def save_model(self, request, obj, form, change):
        # Only auto-approve if user has the permission and checked is_active
        if obj.is_active and request.user.has_perm("yourapp.can_approve_product"):
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)



# -----------------------------
# Variant Admin (Detailed View)
# -----------------------------
@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "size", "stock", "price", "sale_price", "sku")
    list_filter = ("color", "size", "product__brand")
    search_fields = ("sku", "product__name")
    inlines = [ProductImageInline]


# -----------------------------
# Lookup Tables Admin
# -----------------------------
# admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Type)
admin.site.register(Gender)
admin.site.register(Material)
admin.site.register(Color)
admin.site.register(Size)

admin.site.register(Category, DraggableMPTTAdmin)
# admin.site.register(Gender, DraggableMPTTAdmin)
