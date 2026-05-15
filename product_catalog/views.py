from django.shortcuts import render
from .models import Product


def catalog_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'product_catalog/products.html', {'products': products})

