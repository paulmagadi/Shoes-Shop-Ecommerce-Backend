from django.db import models
from django.utils.text import slugify
from django.templatetags.static import static
from mptt.models import MPTTModel, TreeForeignKey
from users.models import CustomUser


# -----------------------------
# Basic Attributes
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

    def __str__(self):
        return " > ".join([c.name for c in self.get_ancestors(include_self=True)])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand-logos/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        return self.logo.url if self.logo else static('images/brand-logos/holder2.png')


class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.name


class Gender(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    class MPTTMeta: order_insertion_by = ['name']
    def __str__(self): return self.name


class Material(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name


class Size(models.Model):
    us_size = models.DecimalField(max_digits=4, decimal_places=1)
    eu_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    uk_size = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    def __str__(self): return f"US {self.us_size}"


class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, null=True, blank=True)
    def __str__(self): return self.name


# -----------------------------
# Product Core
# -----------------------------
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_products')
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='updated_products')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_products')
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [('can_approve_product', 'Can approve product for listing')]

    def __str__(self): return self.name
    
    @property
    def featured_color(self):
        return self.colors.filter(is_featured=True).first()


    def save(self, *args, user=None, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if user and not self.pk:
            self.created_by = user
        if user:
            self.updated_by = user
        super().save(*args, **kwargs)


# -----------------------------
# ProductColor (Color Group)
# -----------------------------
class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    is_featured = models.BooleanField(default=False)
    class Meta:
        unique_together = ('product', 'color')

    def __str__(self):
        return f"{self.product.name} - {self.color.name}"
    
    def save(self, *args, **kwargs):
        if self.is_featured:
            ProductColor.objects.filter(product=self.product, is_featured=True).exclude(id=self.id).update(is_featured=False)
        super().save(*args, **kwargs)



# -----------------------------
# Variant = Color + Size + Stock
# -----------------------------
class Variant(models.Model):
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        unique_together = ('product_color', 'size')

    def __str__(self):
        return f"{self.product_color} - Size {self.size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product_color.product.brand.name[:3].upper()}-{self.product_color.id}-{str(self.size.us_size)}".replace(" ", "")
        super().save(*args, **kwargs)


# -----------------------------
# Product Images (by color group)
# -----------------------------
class ProductImage(models.Model):
    product_color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product-images/')
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Product Images'
        ordering = ['-is_featured', 'id']

    def __str__(self):
        return f"{self.product_color} Image"
    
    def save(self, *args, **kwargs):
        if self.is_featured:
            ProductImage.objects.filter(product_color=self.product_color, is_featured=True).exclude(id=self.id).update(is_featured=False)
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            return self.image.url
        except:
            return ''
