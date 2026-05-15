from rest_framework import serializers

from inventory.models import BulkLot, BulkLotItem, DisposalRecord, ItemInspection, Stock
from product_catalog.models import Category, Product
from sales.models import Sale, SaleItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
        required=False,
    )
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'category_id',
            'specs',
            'image_url',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'image_url', 'category']

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Stock
        fields = [
            'id',
            'product',
            'product_id',
            'quantity',
            'reorder_level',
            'location',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'product']


class BulkLotSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        write_only=True,
    )

    class Meta:
        model = BulkLot
        fields = [
            'id',
            'source_note',
            'category',
            'category_id',
            'acquired_at',
            'total_cost',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'category']


class BulkLotItemSerializer(serializers.ModelSerializer):
    bulk_lot_id = serializers.PrimaryKeyRelatedField(
        source='bulk_lot',
        queryset=BulkLot.objects.all(),
    )
    listed_product = ProductSerializer(read_only=True)

    class Meta:
        model = BulkLotItem
        fields = [
            'id',
            'bulk_lot_id',
            'discovered_name',
            'brand',
            'model',
            'serial_no',
            'status',
            'listed_product',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['listed_product', 'created_at', 'updated_at']


class ItemInspectionSerializer(serializers.ModelSerializer):
    bulk_lot_item_id = serializers.PrimaryKeyRelatedField(
        source='bulk_lot_item',
        queryset=BulkLotItem.objects.all(),
    )
    inspected_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ItemInspection
        fields = [
            'id',
            'bulk_lot_item_id',
            'inspected_by',
            'condition_grade',
            'decision',
            'notes',
            'inspected_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['inspected_by', 'created_at', 'updated_at']


class DisposalRecordSerializer(serializers.ModelSerializer):
    bulk_lot_item_id = serializers.PrimaryKeyRelatedField(
        source='bulk_lot_item',
        queryset=BulkLotItem.objects.all(),
    )
    disposed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DisposalRecord
        fields = [
            'id',
            'bulk_lot_item_id',
            'reason',
            'disposed_by',
            'disposed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['disposed_by', 'created_at', 'updated_at']


class SaleItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.all(),
    )
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = SaleItem
        fields = [
            'id',
            'product',
            'product_id',
            'quantity',
            'unit_price',
            'subtotal',
        ]
        read_only_fields = ['subtotal']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'user',
            'sale_date',
            'total_amount',
            'status',
            'items',
        ]
        read_only_fields = ['id', 'sale_date', 'total_amount', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None

        sale = Sale.objects.create(user=user, **validated_data)

        total_amount = 0
        for item in items_data:
            product = item['product']
            quantity = item['quantity']
            unit_price = item.get('unit_price') or product.price

            sale_item = SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
            )
            total_amount += sale_item.subtotal

        sale.total_amount = total_amount
        sale.save(update_fields=['total_amount'])
        return sale

