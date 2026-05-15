from django.urls import path

from api.views import (
    BulkLotItemListCreateView,
    BulkLotListCreateView,
    DashboardStatsView,
    DisposalRecordCreateView,
    ItemInspectionCreateView,
    ListingApprovalView,
    PendingInspectionItemsView,
    ProductListView,
    SalesListCreateView,
    StockListView,
)


urlpatterns = [
    path('products/', ProductListView.as_view(), name='api_products'),
    path('stocks/', StockListView.as_view(), name='api_stocks'),
    path('bulk-lots/', BulkLotListCreateView.as_view(), name='api_bulk_lots'),
    path('bulk-items/', BulkLotItemListCreateView.as_view(), name='api_bulk_items'),
    path('bulk-items/pending-inspection/', PendingInspectionItemsView.as_view(), name='api_bulk_items_pending'),
    path('bulk-items/inspect/', ItemInspectionCreateView.as_view(), name='api_item_inspection'),
    path('bulk-items/<int:item_id>/approve-listing/', ListingApprovalView.as_view(), name='api_listing_approval'),
    path('bulk-items/dispose/', DisposalRecordCreateView.as_view(), name='api_disposal'),
    path('dashboard/', DashboardStatsView.as_view(), name='api_dashboard'),
    path('sales/', SalesListCreateView.as_view(), name='api_sales'),
]

