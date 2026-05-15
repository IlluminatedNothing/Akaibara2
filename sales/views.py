from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from auth_custom.views import role_required


@login_required
@role_required(['admin', 'cashier'])
def sales_home(request):
    # Render sales page
    return render(request, 'sales/sales.html')


@login_required
@role_required(['admin', 'cashier'])
def sales_pos(request):
    # Render cashier/POS page
    return render(request, 'sales/cashier.html')


@login_required
@role_required(['admin', 'cashier'])
def payments(request):
    # Render payments page
    return render(request, 'sales/payments.html')


