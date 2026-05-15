from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard_root'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('reports/', views.dashboard, name='reports'),  # Placeholder
]

