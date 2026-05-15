from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from auth_custom.views import role_required


@login_required
@role_required(['admin', 'cashier'])
def cashier_view(request):
    # Redirect to the proper sales POS page
    return redirect('sales_pos')


@login_required
@role_required(['admin', 'cashier'])
def payments_view(request):
    # Redirect to the proper sales payments page
    return redirect('sales_payments')


@login_required
@role_required(['admin', 'inspector'])
def item_inspection_view(request):
    # Redirect to the proper inventory item inspection page
    return redirect('inventory_item_inspection')

