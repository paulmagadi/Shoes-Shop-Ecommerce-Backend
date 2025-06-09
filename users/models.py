from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from users.managers import CustomUserManager
from django.templatetags.static import static


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_email_verified = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='uploads/users', null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = "Users"
    
    # def generate_email_verification_token(self):
    #     return str(uuid.uuid4())
    
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
 



