from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm

from django.utils.translation import gettext_lazy as _
from .models import CustomUser, BillingAddress

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_email_verified')
    list_filter = ('is_active', 'is_staff', 'is_email_verified')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'profile_image')}),
        (_('Verification'), {'fields': ('is_email_verified',)}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ("groups", "user_permissions",)
    readonly_fields = ("id", "last_login", "date_joined",)


admin.site.register(BillingAddress)