from rest_framework.routers import DefaultRouter
from django.urls import path, include
from travel.views import (
    NavanApiConfigViewSet, SyncedUserViewSet, BookingViewSet,
    ImportLogViewSet, TravelDashboardViewSet, ImportViewSet
)

router = DefaultRouter()
router.register(r'api-config', NavanApiConfigViewSet, basename='api-config')
router.register(r'users', SyncedUserViewSet, basename='synced-user')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'import-logs', ImportLogViewSet, basename='import-log')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/analytics/', TravelDashboardViewSet.as_view({'get': 'analytics'}), name='dashboard-analytics'),
    path('dashboard/monthly-trend/', TravelDashboardViewSet.as_view({'get': 'monthly-trend'}), name='dashboard-monthly-trend'),
    path('dashboard/status-distribution/', TravelDashboardViewSet.as_view({'get': 'status-distribution'}), name='dashboard-status-distribution'),
    path('dashboard/department-spend/', TravelDashboardViewSet.as_view({'get': 'department-spend'}), name='dashboard-department-spend'),
    path('dashboard/region-bookings/', TravelDashboardViewSet.as_view({'get': 'region-bookings'}), name='dashboard-region-bookings'),
    path('dashboard/booking-type-comparison/', TravelDashboardViewSet.as_view({'get': 'booking-type-comparison'}), name='dashboard-booking-type-comparison'),
    path('dashboard/recent-imports/', TravelDashboardViewSet.as_view({'get': 'recent-imports'}), name='dashboard-recent-imports'),
    path('import/sync-users/', ImportViewSet.as_view({'post': 'sync_users'}), name='import-sync-users'),
    path('import/bookings/', ImportViewSet.as_view({'post': 'import_bookings'}), name='import-bookings'),
    path('import/reconciliation/', ImportViewSet.as_view({'post': 'daily_reconciliation'}), name='import-reconciliation'),
]