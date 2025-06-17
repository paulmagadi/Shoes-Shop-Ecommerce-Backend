from django.shortcuts import render
from store.models import Product

def home(request):
    products = Product.objects.filter(is_active=True, is_archived=False)\
        .prefetch_related('colors__color', 'colors__images', 'colors__variants__size')\
        .select_related('brand')

    return render(request, 'main/home.html', {'products': products})
