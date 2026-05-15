from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import BulkLot, BulkLotItem, DisposalRecord, ItemInspection, Stock
from product_catalog.models import Product
from sales.models import Sale
from api.serializers import (
    BulkLotItemSerializer,
    BulkLotSerializer,
    DisposalRecordSerializer,
    ItemInspectionSerializer,
    ProductSerializer,
    SaleSerializer,
    StockSerializer,
)


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.AllowAny]


class BulkLotListCreateView(generics.ListCreateAPIView):
    queryset = BulkLot.objects.all().order_by('-acquired_at', '-id')
    serializer_class = BulkLotSerializer
    permission_classes = [permissions.AllowAny]


class BulkLotItemListCreateView(generics.ListCreateAPIView):
    queryset = BulkLotItem.objects.select_related('bulk_lot', 'listed_product').all().order_by('-id')
    serializer_class = BulkLotItemSerializer
    permission_classes = [permissions.AllowAny]


class PendingInspectionItemsView(generics.ListAPIView):
    serializer_class = BulkLotItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return BulkLotItem.objects.select_related('bulk_lot', 'listed_product').filter(
            status__in=[
                BulkLotItem.STATUS_PENDING,
                BulkLotItem.STATUS_FOR_INSPECTION,
                BulkLotItem.STATUS_HOLD,
            ]
        ).order_by('-id')


class ItemInspectionCreateView(generics.CreateAPIView):
    queryset = ItemInspection.objects.all()
    serializer_class = ItemInspectionSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        inspection = serializer.save(
            inspected_by=self.request.user if self.request.user.is_authenticated else None
        )
        status_map = {
            ItemInspection.DECISION_FOR_SALE: BulkLotItem.STATUS_APPROVED_FOR_SALE,
            ItemInspection.DECISION_FOR_REPAIR: BulkLotItem.STATUS_FOR_REPAIR,
            ItemInspection.DECISION_DISPOSE: BulkLotItem.STATUS_DISPOSED,
            ItemInspection.DECISION_HOLD: BulkLotItem.STATUS_HOLD,
        }
        new_status = status_map.get(inspection.decision, BulkLotItem.STATUS_FOR_INSPECTION)
        BulkLotItem.objects.filter(id=inspection.bulk_lot_item_id).update(status=new_status)


class ListingApprovalView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, item_id):
        try:
            bulk_item = BulkLotItem.objects.select_related('bulk_lot__category', 'listed_product').get(id=item_id)
        except BulkLotItem.DoesNotExist:
            return Response({'detail': 'Bulk item not found.'}, status=status.HTTP_404_NOT_FOUND)

        if bulk_item.listed_product_id:
            return Response({'detail': 'Item is already listed as a product.'}, status=status.HTTP_400_BAD_REQUEST)

        if bulk_item.status not in [BulkLotItem.STATUS_APPROVED_FOR_SALE, BulkLotItem.STATUS_HOLD]:
            return Response(
                {'detail': 'Item must be approved for sale or on hold before listing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = request.data
        name = payload.get('name') or bulk_item.discovered_name
        price = payload.get('price')
        if not name or price is None:
            return Response({'detail': 'Both name and price are required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.create(
            name=name,
            description=payload.get('description', 'Listed from bulk inventory processing.'),
            price=price,
            category=bulk_item.bulk_lot.category,
            specs=payload.get('specs', ''),
        )
        bulk_item.listed_product = product
        bulk_item.status = BulkLotItem.STATUS_APPROVED_FOR_SALE
        bulk_item.save(update_fields=['listed_product', 'status', 'updated_at'])
        Stock.objects.get_or_create(product=product, defaults={'quantity': 1, 'reorder_level': 0})

        return Response(ProductSerializer(product, context={'request': request}).data, status=status.HTTP_201_CREATED)


class DisposalRecordCreateView(generics.CreateAPIView):
    queryset = DisposalRecord.objects.all()
    serializer_class = DisposalRecordSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        disposal = serializer.save(
            disposed_by=self.request.user if self.request.user.is_authenticated else None
        )
        BulkLotItem.objects.filter(id=disposal.bulk_lot_item_id).update(status=BulkLotItem.STATUS_DISPOSED)


class DashboardStatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Lightweight metrics to power the dashboard.
        return Response(
            {
                'total_sales': Sale.objects.count(),
                'low_stock': Stock.objects.filter(quantity__lte=10).count(),
                'total_products': Product.objects.count(),
                'pending_inspections': BulkLotItem.objects.filter(
                    status__in=[BulkLotItem.STATUS_PENDING, BulkLotItem.STATUS_FOR_INSPECTION]
                ).count(),
                'disposed_items': DisposalRecord.objects.count(),
            },
            status=status.HTTP_200_OK,
        )


class SalesListCreateView(generics.ListCreateAPIView):
    queryset = Sale.objects.all().order_by('-id')
    serializer_class = SaleSerializer
    permission_classes = [permissions.AllowAny]

