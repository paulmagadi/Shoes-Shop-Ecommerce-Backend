# orders/forms.py
from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'full_name', 'address', 'alternative_address',
            'city', 'postal_code', 'country', 'phone', 'is_primary'
        ]
