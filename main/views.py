from django.shortcuts import render, get_object_or_404
from store.models import Product, ProductImage, Variant

# Create your views here.

def home(request):
    products = Product.objects.filter(is_active=True, is_archived=False).order_by('-created_at')[:12]
    return render(request, 'main/home.html', {'products': products})