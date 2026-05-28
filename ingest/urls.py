from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ImportBatchViewSet,
    NormalizedRecordViewSet,
    ValidationIssueViewSet,
    dashboard_view,
    login_view,
    me_view,
    upload_csv_view,
)

from .sap_views import (
    sap_upload_csv_view,
    sap_dashboard_view,
    SAPRecordViewSet,
    SAPValidationIssueViewSet,
    SAPApprovalLogViewSet,
    SAPImportBatchViewSet,
)

# Main router for utility dashboard
router = DefaultRouter()
router.register('uploads', ImportBatchViewSet, basename='uploads')
router.register('records', NormalizedRecordViewSet, basename='records')
router.register('issues', ValidationIssueViewSet, basename='issues')

# SAP router for procurement dashboard
sap_router = DefaultRouter()
sap_router.register('sap/records', SAPRecordViewSet, basename='sap-records')
sap_router.register('sap/issues', SAPValidationIssueViewSet, basename='sap-issues')
sap_router.register('sap/approval-logs', SAPApprovalLogViewSet, basename='sap-approval-logs')
sap_router.register('sap/batches', SAPImportBatchViewSet, basename='sap-batches')

urlpatterns = [
    # Auth endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/me/', me_view, name='me'),
    
    # Utility Dashboard endpoints
    path('dashboard/', dashboard_view, name='dashboard'),
    path('upload/', upload_csv_view, name='upload'),
    
    # SAP Procurement Dashboard endpoints
    path('sap/dashboard/', sap_dashboard_view, name='sap-dashboard'),
    path('sap/upload/', sap_upload_csv_view, name='sap-upload'),
    
    # Routers
    path('', include(router.urls)),
    path('', include(sap_router.urls)),
]
