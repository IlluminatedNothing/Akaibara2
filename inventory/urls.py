from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_home, name='inventory_home'),
    path('bulk-lots/', views.bulk_lots, name='inventory_bulk_lots'),
    path('item-inspection/', views.item_inspection, name='inventory_item_inspection'),
]

