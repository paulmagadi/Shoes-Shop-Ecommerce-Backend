from django.db import models
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image
from django.templatetags.static import static
from mptt.models import MPTTModel, TreeForeignKey



from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify

# ----------------------
# Category (Hierarchical)
# ----------------------
class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


# ----------------------
# Other Lookups
# ----------------------
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(
        max_length=50,
        choices=[('men', 'Men'), ('women', 'Women'), ('unisex', 'Unisex'), ('kids', 'Kids'), ('baby', 'Baby')]
    )

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# ----------------------
# Core Product Model
# ----------------------

class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()

    def unarchive(self):
        self.is_archived = False
        self.archived_at = None
        self.save()

    objects = ProductManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ----------------------
# Product Image Model
# ----------------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product-images/')
    is_thumbnail = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} Image"


# ----------------------
# Variants, Size, Color
# ----------------------
class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_value = models.CharField(max_length=7, blank=True, null=True)  # Optional color preview

    def __str__(self):
        return self.name


class Size(models.Model):
    size = models.CharField(max_length=10)  # e.g., "42", "10.5", "M", "XL"

    def __str__(self):
        return self.size


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.size.size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.brand.name[:3].upper()}-{self.product.id}-{self.color.name[:3].upper()}-{self.size.size}".replace(" ", "")
        super().save(*args, **kwargs)
