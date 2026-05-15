from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from auth_custom.views import role_required
from inventory.forms import (
    ApproveItemForm,
    CreateBulkLotForm,
    DisposeItemForm,
    RepairItemForm,
)
from inventory.models import (
    BulkLot,
    BulkLotItem,
    DisposalRecord,
    ItemInspection,
    Stock,
    StockMovement,
)
from product_catalog.models import Category, Product


@login_required
@role_required(['admin', 'cashier'])
def inventory_home(request):
    stocks = Stock.objects.select_related('product__category').all()
    context = {
        'stocks': stocks,
        'total_stock_records': stocks.count(),
        'low_stock_count': stocks.filter(quantity__lte=10).count(),
        'pending_sorting_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_PENDING).count(),
        'pending_inspection_count': BulkLotItem.objects.filter(
            status=BulkLotItem.STATUS_FOR_INSPECTION
        ).count(),
        'approved_for_sale_count': BulkLotItem.objects.filter(
            status=BulkLotItem.STATUS_APPROVED_FOR_SALE
        ).count(),
        'for_repair_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_FOR_REPAIR).count(),
        'disposed_count': DisposalRecord.objects.count(),
    }
    return render(request, 'inventory/inventory.html', context)


@login_required
@role_required(['admin', 'cashier'])
def bulk_lots(request):
    create_form = CreateBulkLotForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_bulk_lot':
            create_form = CreateBulkLotForm(request.POST)
            if create_form.is_valid():
                bulk_lot = create_form.save(commit=False)
                bulk_lot.save()
                timestamp = timezone.now()
                items = [
                    BulkLotItem(
                        bulk_lot=bulk_lot,
                        discovered_name=f'{bulk_lot.category.name} Item {index}',
                        status=BulkLotItem.STATUS_PENDING,
                        created_at=timestamp,
                        updated_at=timestamp,
                    )
                    for index in range(1, 11)
                ]
                BulkLotItem.objects.bulk_create(items)
                messages.success(request, 'Bulk lot created with 10 pending items.')
                return redirect('inventory_bulk_lots')
            else:
                messages.error(request, 'Please fix the form errors before creating the bulk lot.')

        elif action == 'release_lot':
            lot_id = request.POST.get('lot_id')
            bulk_lot = get_object_or_404(BulkLot, id=lot_id)
            pending_items = bulk_lot.items.filter(status=BulkLotItem.STATUS_PENDING)
            if pending_items.exists():
                pending_items.update(status=BulkLotItem.STATUS_FOR_INSPECTION)
                messages.success(request, 'Bulk lot released for inspection.')
            else:
                messages.warning(request, 'No pending items were found to release.')
            return redirect('inventory_bulk_lots')

    lots = BulkLot.objects.select_related('category').annotate(
        item_count=Count('items'),
        pending_count=Count('items', filter=Q(items__status=BulkLotItem.STATUS_PENDING)),
        inspection_count=Count('items', filter=Q(items__status=BulkLotItem.STATUS_FOR_INSPECTION)),
    ).order_by('-acquired_at', '-id')

    context = {
        'create_form': create_form,
        'lots': lots,
        'categories': Category.objects.all(),
        'pending_sorting_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_PENDING).count(),
        'for_inspection_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_FOR_INSPECTION).count(),
    }
    return render(request, 'inventory/bulk_lots.html', context)


@login_required
@role_required(['admin', 'inspector'])
def item_inspection(request):
    approve_form = ApproveItemForm()
    repair_form = RepairItemForm()
    dispose_form = DisposeItemForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            approve_form = ApproveItemForm(request.POST)
            if approve_form.is_valid():
                item = get_object_or_404(
                    BulkLotItem,
                    id=approve_form.cleaned_data['item_id'],
                    status__in=[
                        BulkLotItem.STATUS_FOR_INSPECTION,
                        BulkLotItem.STATUS_FOR_REPAIR,
                        BulkLotItem.STATUS_HOLD,
                    ],
                )
                product = Product.objects.create(
                    name=approve_form.cleaned_data['product_name'],
                    description=approve_form.cleaned_data['description'] or '',
                    price=approve_form.cleaned_data['price'],
                    category=item.bulk_lot.category,
                    specs=approve_form.cleaned_data['specs'] or '',
                )
                stock, created = Stock.objects.get_or_create(
                    product=product,
                    defaults={
                        'quantity': 1,
                        'location': approve_form.cleaned_data['stock_location'],
                        'reorder_level': 0,
                    },
                )
                if not created:
                    stock.quantity += 1
                    stock.location = approve_form.cleaned_data['stock_location']
                    stock.save()

                StockMovement.objects.create(
                    product=product,
                    movement_type='in',
                    quantity=1,
                    reference_id=item.id,
                    reference_type='bulk_lot_item',
                    notes='Approved for sale',
                    user=request.user,
                )

                item.discovered_name = approve_form.cleaned_data['discovered_name']
                item.brand = approve_form.cleaned_data['brand']
                item.model = approve_form.cleaned_data['model']
                item.serial_no = approve_form.cleaned_data['serial_no'] or ''
                item.status = BulkLotItem.STATUS_APPROVED_FOR_SALE
                item.listed_product = product
                item.save()

                ItemInspection.objects.create(
                    bulk_lot_item=item,
                    inspected_by=request.user,
                    condition_grade=approve_form.cleaned_data['condition_grade'],
                    decision=ItemInspection.DECISION_FOR_SALE,
                    notes='Approved for sale',
                    inspected_at=timezone.now(),
                )

                messages.success(request, 'Item approved and listed for sale.')
                return redirect('inventory_item_inspection')
            messages.error(request, 'Please fix the approve form errors.')

        elif action == 'repair':
            repair_form = RepairItemForm(request.POST)
            if repair_form.is_valid():
                item = get_object_or_404(
                    BulkLotItem,
                    id=repair_form.cleaned_data['item_id'],
                    status=BulkLotItem.STATUS_FOR_INSPECTION,
                )
                item.discovered_name = request.POST.get('discovered_name', item.discovered_name)
                item.status = BulkLotItem.STATUS_FOR_REPAIR
                item.save()
                ItemInspection.objects.create(
                    bulk_lot_item=item,
                    inspected_by=request.user,
                    condition_grade=repair_form.cleaned_data['condition_grade'],
                    decision=ItemInspection.DECISION_FOR_REPAIR,
                    notes=repair_form.cleaned_data['notes'] or '',
                    inspected_at=timezone.now(),
                )
                messages.success(request, 'Item marked for repair.')
                return redirect('inventory_item_inspection')
            messages.error(request, 'Please fix the repair form errors.')

        elif action == 'dispose':
            dispose_form = DisposeItemForm(request.POST)
            if dispose_form.is_valid():
                item = get_object_or_404(
                    BulkLotItem,
                    id=dispose_form.cleaned_data['item_id'],
                    status=BulkLotItem.STATUS_FOR_INSPECTION,
                )
                item.discovered_name = request.POST.get('discovered_name', item.discovered_name)
                item.status = BulkLotItem.STATUS_DISPOSED
                item.save()
                ItemInspection.objects.create(
                    bulk_lot_item=item,
                    inspected_by=request.user,
                    condition_grade=dispose_form.cleaned_data['condition_grade'],
                    decision=ItemInspection.DECISION_DISPOSE,
                    notes=dispose_form.cleaned_data['disposal_reason'],
                    inspected_at=timezone.now(),
                )
                DisposalRecord.objects.create(
                    bulk_lot_item=item,
                    reason=dispose_form.cleaned_data['disposal_reason'],
                    disposed_by=request.user,
                    disposed_at=timezone.now(),
                )
                messages.success(request, 'Item disposed and inspection recorded.')
                return redirect('inventory_item_inspection')
            messages.error(request, 'Please fix the disposal form errors.')

        elif action == 'hold':
            item_id = request.POST.get('item_id')
            item = get_object_or_404(
                BulkLotItem,
                id=item_id,
                status=BulkLotItem.STATUS_FOR_INSPECTION,
            )
            item.discovered_name = request.POST.get('discovered_name', item.discovered_name)
            item.status = BulkLotItem.STATUS_HOLD
            item.save()
            ItemInspection.objects.create(
                bulk_lot_item=item,
                inspected_by=request.user,
                condition_grade=ItemInspection.GRADE_C,
                decision=ItemInspection.DECISION_HOLD,
                notes='Put on hold for future review',
                inspected_at=timezone.now(),
            )
            messages.success(request, 'Item placed on hold.')
            return redirect('inventory_item_inspection')

    items = BulkLotItem.objects.filter(status=BulkLotItem.STATUS_FOR_INSPECTION).select_related('bulk_lot__category')
    repair_items = BulkLotItem.objects.filter(status=BulkLotItem.STATUS_FOR_REPAIR).select_related('bulk_lot__category')
    hold_items = BulkLotItem.objects.filter(status=BulkLotItem.STATUS_HOLD).select_related('bulk_lot__category')
    disposed_items = BulkLotItem.objects.filter(status=BulkLotItem.STATUS_DISPOSED).select_related('bulk_lot__category')
    context = {
        'items': items,
        'repair_items': repair_items,
        'hold_items': hold_items,
        'disposed_items': disposed_items,
        'approve_form': approve_form,
        'repair_form': repair_form,
        'dispose_form': dispose_form,
        'pending_inspection_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_FOR_INSPECTION).count(),
        'approved_count': BulkLotItem.objects.filter(status=BulkLotItem.STATUS_APPROVED_FOR_SALE).count(),
    }
    return render(request, 'inventory/item_inspection.html', context)

