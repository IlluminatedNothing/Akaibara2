from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sales.models import Sale
from product_catalog.models import Product
from inventory.models import Stock

from auth_custom.views import role_required


@role_required(['admin', 'cashier', 'inspector'])
def dashboard(request):



    context = {
        'total_sales': Sale.objects.count(),
        'low_stock': Stock.objects.filter(quantity__lte=10).count(),
        'total_products': Product.objects.count(),
    }
    return render(request, 'reports_dashboard/dashboard.html', context)

