from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_home, name='sales_home'),
    path('pos/', views.sales_pos, name='sales_pos'),
    path('payments/', views.payments, name='sales_payments'),
]

