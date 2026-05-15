from django.urls import path
from . import views

urlpatterns = [
    path('cashier/', views.cashier_view, name='cashier'),
    path('payments/', views.payments_view, name='payments'),
    path('item-inspection/', views.item_inspection_view, name='item_inspection'),
]


