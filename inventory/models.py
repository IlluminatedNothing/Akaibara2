from django.db import models
from core.models import BaseModel
from django.contrib.auth.models import User
from product_catalog.models import Category, Product


class Stock(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    location = models.CharField(max_length=100, blank=True)  # Shelf, warehouse

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    class Meta:
        unique_together = ['product']


class StockMovement(models.Model):
    stock_movement_id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    reference_id = models.BigIntegerField(null=True, blank=True)
    reference_type = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stock_movements'
        managed = False


class BulkLot(BaseModel):
    source_note = models.CharField(max_length=150, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    acquired_at = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"Lot #{self.id} ({self.category.name})"


class BulkLotItem(BaseModel):
    STATUS_PENDING = 'pending'
    STATUS_FOR_INSPECTION = 'for_inspection'
    STATUS_APPROVED_FOR_SALE = 'approved_for_sale'
    STATUS_FOR_REPAIR = 'for_repair'
    STATUS_DISPOSED = 'disposed'
    STATUS_HOLD = 'hold'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_FOR_INSPECTION, 'For Inspection'),
        (STATUS_APPROVED_FOR_SALE, 'Approved for Sale'),
        (STATUS_FOR_REPAIR, 'For Repair'),
        (STATUS_DISPOSED, 'Disposed'),
        (STATUS_HOLD, 'Hold'),
    ]

    bulk_lot = models.ForeignKey(BulkLot, on_delete=models.CASCADE, related_name='items')
    discovered_name = models.CharField(max_length=150, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_no = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    listed_product = models.OneToOneField(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='source_bulk_item',
    )

    def __str__(self):
        label = self.discovered_name or f"Bulk item #{self.id}"
        return f"{label} [{self.status}]"


class ItemInspection(BaseModel):
    DECISION_FOR_SALE = 'for_sale'
    DECISION_FOR_REPAIR = 'for_repair'
    DECISION_DISPOSE = 'dispose'
    DECISION_HOLD = 'hold'
    DECISION_CHOICES = [
        (DECISION_FOR_SALE, 'For Sale'),
        (DECISION_FOR_REPAIR, 'For Repair'),
        (DECISION_DISPOSE, 'Dispose'),
        (DECISION_HOLD, 'Hold'),
    ]
    GRADE_A = 'A'
    GRADE_B = 'B'
    GRADE_C = 'C'
    GRADE_D = 'D'
    GRADE_E = 'E'
    GRADE_CHOICES = [
        (GRADE_A, 'A'),
        (GRADE_B, 'B'),
        (GRADE_C, 'C'),
        (GRADE_D, 'D'),
        (GRADE_E, 'E'),
    ]

    bulk_lot_item = models.ForeignKey(
        BulkLotItem,
        on_delete=models.CASCADE,
        related_name='inspections',
    )
    inspected_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    condition_grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES)
    notes = models.TextField(blank=True)
    inspected_at = models.DateTimeField()

    def __str__(self):
        return f"Inspection #{self.id} ({self.decision})"


class DisposalRecord(BaseModel):
    bulk_lot_item = models.OneToOneField(
        BulkLotItem,
        on_delete=models.CASCADE,
        related_name='disposal_record',
    )
    reason = models.TextField()
    disposed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    disposed_at = models.DateTimeField()

    def __str__(self):
        return f"Disposal #{self.id} for item #{self.bulk_lot_item_id}"

