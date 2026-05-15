import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from auth_custom.views import role_required
from inventory.models import Stock, StockMovement
from product_catalog.models import Product
from sales.models import Payment, Sale, SaleItem


@login_required
@role_required(['admin', 'cashier'])
def sales_home(request):
    sales = Sale.objects.select_related('user').annotate(
        item_count=Count('items')
    ).order_by('-sale_date')
    context = {
        'sales': sales,
    }
    return render(request, 'sales/sales.html', context)


@login_required
@role_required(['admin', 'cashier'])
def sales_pos(request):
    products = []
    stock_map = {}

    for stock in Stock.objects.select_related('product__category').all():
        stock_map[stock.product.id] = stock.quantity

    for product in Product.objects.select_related('category').all():
        product.current_stock = stock_map.get(product.id, 0)
        if product.current_stock > 0:
            products.append(product)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'checkout':
            cart_data = request.POST.get('cart_data', '[]')
            try:
                cart_items = json.loads(cart_data)
            except json.JSONDecodeError:
                cart_items = []

            if not cart_items:
                messages.error(request, 'Your cart is empty. Add items before checking out.')
                return redirect('sales_pos')

            validation_items = []
            subtotal = Decimal('0.00')

            for item in cart_items:
                product_id = int(item.get('id', 0))
                quantity = int(item.get('quantity', 0))
                unit_price = Decimal(str(item.get('price', '0')))

                if quantity <= 0:
                    continue

                product = get_object_or_404(Product, id=product_id)
                stock = Stock.objects.filter(product=product).first()
                current_quantity = stock.quantity if stock else 0

                if current_quantity < quantity:
                    messages.error(request, f'Insufficient stock for {product.name}.')
                    return redirect('sales_pos')

                subtotal += unit_price * quantity
                validation_items.append((product, quantity, unit_price, stock))

            if not validation_items:
                messages.error(request, 'Your cart is empty. Add items before checking out.')
                return redirect('sales_pos')

            with transaction.atomic():
                sale = Sale.objects.create(user=request.user, status='completed')

                for product, quantity, unit_price, stock in validation_items:
                    sale_item = SaleItem(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                    sale_item.save()

                    if stock:
                        stock.quantity -= quantity
                        stock.save()

                    StockMovement.objects.create(
                        product=product,
                        movement_type='sale',
                        quantity=quantity,
                        reference_type='sale',
                        reference_id=sale.id,
                        user=request.user,
                    )

                tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
                total_amount = (subtotal + tax).quantize(Decimal('0.01'))
                sale.total_amount = total_amount
                sale.save()

                Payment.objects.create(
                    sale=sale,
                    payment_method='cash',
                    amount=total_amount,
                )

            messages.success(request, f'Sale completed successfully. Sale #{sale.id} created.')
            return redirect('sales_pos')

    context = {
        'products': products,
    }
    return render(request, 'sales/cashier.html', context)


@login_required
@role_required(['admin', 'cashier'])
def payments(request):
    payments = Payment.objects.select_related('sale', 'sale__user').order_by('-paid_at')
    context = {
        'payments': payments,
    }
    return render(request, 'sales/payments.html', context)


