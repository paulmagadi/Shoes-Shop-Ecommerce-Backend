from django.db.models import Q
from django.shortcuts import render
from store.models import Product, Variant, ProductColor

def product_search_view(request):
    query = request.GET.get("q", "").strip()
    results = []

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(colors__color__name__icontains=query),
            is_active=True,
            is_archived=False
        ).select_related("brand", "category").prefetch_related("colors__color").distinct()

    return render(request, "store/search_results.html", {
        "query": query,
        "results": results,
    })
