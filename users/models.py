from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save, pre_save
from django.templatetags.static import static

from django.dispatch import receiver
import uuid
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='users/', null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()
    
    
    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def imageURL(self):
        if self.profile_image:
            return self.profile_image.url
        return static('images/user.png')



# class EmailVerificationToken(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     token = models.CharField(max_length=255, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()

#     def is_expired(self):
#         return timezone.now() > self.expires_at
 


class BillingAddress(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="billing_address")
    phone = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name_plural = 'Billing Address'


@receiver(post_save, sender=CustomUser)
def handle_billing_address(sender, instance, created, **kwargs):
    if created:
        BillingAddress.objects.create(
            user=instance,
            full_name=f"{instance.first_name} {instance.last_name}",
            email=instance.email
        )
    else:
        try:
            billing = instance.billing_address
            billing.full_name = f"{instance.first_name} {instance.last_name}"
            billing.email = instance.email
            billing.save()
        except BillingAddress.DoesNotExist:
            BillingAddress.objects.create(
                user=instance,
                full_name=f"{instance.first_name} {instance.last_name}",
                email=instance.email
            )

