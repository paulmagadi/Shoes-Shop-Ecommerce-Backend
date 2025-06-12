from django.conf import settings
from django.db import models
from datetime import timedelta
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from PIL import Image
from django.templatetags.static import static
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from django.utils import timezone
from users.models import CustomUser

# -----------------------------
# Lookups & Attributes
# -----------------------------
class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        unique_together = ('parent', 'name')
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_full_path(self):
        ancestors = self.get_ancestors(include_self=True)
        return " > ".join([category.name for category in ancestors])

    def __str__(self):
        return self.get_full_path()


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand-logos/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        if self.logo:
            return self.logo.url
        return static('images/brand/holder2.png')


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Gender(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name


class Size(models.Model):
    us_size = models.DecimalField(max_digits=4, decimal_places=1)
    eu_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    uk_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return f"US {self.us_size}"


# -----------------------------
# Core Product Model
# -----------------------------
class ProductManager(models.Manager):
    def active(self):
        return self.filter(is_active=True, is_archived=False)

    def archived(self):
        return self.filter(is_archived=True)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_products')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_products')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_products'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    objects = ProductManager()
    class Meta:
        permissions = [
            ('can_approve_product', 'Can approve product for listing'),
        ]

    def __str__(self):
        return self.name

    def archive(self):
        self.is_archived = True
        self.archived_at = timezone.now()
        self.save()

    def unarchive(self):
        self.is_archived = False
        self.archived_at = None
        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def save(self, *args, user=None, **kwargs):
        if user and not self.pk:
            self.created_by = user
        if user:
            self.updated_by = user
        super().save(*args, **kwargs)



# -----------------------------
# Variant and Images
# -----------------------------
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=50, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.brand.name[:3].upper()}-{self.product.id}-{self.color.name[:3].upper()}-{str(self.size.us_size)}".replace(" ", "")
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product-images/')
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Product Images'
        ordering = ['-is_featured', 'id']

    def __str__(self):
        return f"{self.variant.product.name} - {self.variant.color.name} Image"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            return self.image.url
        except:
            return ''


@receiver(pre_save, sender=ProductImage)
def resize_image(sender, instance, **kwargs):
    if instance.image:
        try:
            img = Image.open(instance.image)
            if img.height > 1125 or img.width > 1125:
                img.thumbnail((1125, 1125))
                img.save(instance.image.path, quality=70, optimize=True)
        except Exception as e:
            print(f"Error resizing image: {e}")
