from django.contrib import admin
from .models import (
    Category, Brand, Type, Gender, Material, Color, Size,
    Product, ProductColor, Variant, ProductImage
)
from django.utils.html import format_html
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
    fields = ('size', 'stock', 'price', 'sale_price', 'sku')
    readonly_fields = ('sku',)


class ProductColorInline(admin.StackedInline):
    model = ProductColor
    extra = 1
    show_change_link = True
    inlines = []  # We’ll register its children separately
    verbose_name_plural = "Colors for Product"


    # Custom method to include Variant & Images under ProductColor (requires nested admin or manual management)
    def get_inline_instances(self, request, obj=None):
        return super().get_inline_instances(request, obj)


# -----------------------------
# Product Admin
# -----------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "is_active", "is_archived", "approved_by", "approved_at", "created_at")
    list_filter = ("is_active", "is_archived", "brand", "category")
    readonly_fields = ("approved_by", "approved_at")
    search_fields = ("name", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductColorInline]
    actions = ['approve_selected_products']

    def approve_selected_products(self, request, queryset):
        if not request.user.has_perm("store.can_approve_product"):
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
        if obj.is_active and request.user.has_perm("store.can_approve_product"):
            obj.approved_by = request.user
            obj.approved_at = timezone.now()
        super().save_model(request, obj, form, change)


# -----------------------------
# ProductColor Admin
# -----------------------------
@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "is_featured")
    list_editable = ("is_featured",)
    inlines = [ProductImageInline, VariantInline]


# -----------------------------
# Variant Admin (optional direct)
# -----------------------------
@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("product_color", "size", "stock", "price", "sale_price", "sku")
    list_filter = ("product_color__product__brand", "product_color__color")
    search_fields = ("sku", "product_color__product__name")


# -----------------------------
# Lookup Tables Admin
# -----------------------------
admin.site.register(Brand)
admin.site.register(Type)
admin.site.register(Gender)
admin.site.register(Material)
admin.site.register(Color)
admin.site.register(Size)

admin.site.register(Category, DraggableMPTTAdmin)
