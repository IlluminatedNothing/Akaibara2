from django import forms

from inventory.models import BulkLot, ItemInspection
from product_catalog.models import Category


class CreateBulkLotForm(forms.ModelForm):
    acquired_at = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Acquired Date',
    )
    total_cost = forms.DecimalField(
        min_value=0,
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control decimal-input',
            'step': '0.01',
            'inputmode': 'decimal',
            'placeholder': '0.00',
        }),
        label='Total Cost',
    )

    class Meta:
        model = BulkLot
        fields = ['source_note', 'category', 'acquired_at', 'total_cost', 'remarks']
        widgets = {
            'source_note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Source or note'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks'}),
        }
        labels = {
            'source_note': 'Source / Note',
            'remarks': 'Remarks',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = 'Select a category'


class ApproveItemForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    discovered_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Discovered name',
    )
    brand = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )
    model = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )
    serial_no = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
        label='Serial Number',
    )
    condition_grade = forms.ChoiceField(
        choices=ItemInspection.GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Condition Grade',
    )
    product_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Product Name',
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
    )
    price = forms.DecimalField(
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control decimal-input',
            'step': '0.01',
            'inputmode': 'decimal',
            'placeholder': '0.00',
        }),
    )
    specs = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label='Specs',
    )
    stock_location = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        initial='Shelf A',
        label='Stock Location',
    )


class RepairItemForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    condition_grade = forms.ChoiceField(
        choices=ItemInspection.GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Condition Grade',
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Repair notes'}),
    )


class DisposeItemForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)
    condition_grade = forms.ChoiceField(
        choices=ItemInspection.GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Condition Grade',
    )
    disposal_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Disposal reason'}),
        label='Disposal Reason',
    )
