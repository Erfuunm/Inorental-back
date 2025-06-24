from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

app_name = 'financial'

# Schema view for Swagger/OpenAPI
docs_schema_view = get_schema_view(
    openapi.Info(
        title="Financial API",
        default_version='v1',
        description="API for managing financial transactions and QuickBooks integration",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Create a router for ViewSets
router = DefaultRouter()

# API URL patterns
api_urlpatterns = [
    # Payment endpoints
    path('payments/', views.PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<int:id>/', views.PaymentRetrieveUpdateDestroyView.as_view(), name='payment-detail'),
    path('payments/sync/', views.SyncPaymentsView.as_view(), name='payment-sync'),
    path('payments/download-records/', views.DownloadFinancialRecordsView.as_view(), name='download-records'),
    
    # Rent request endpoints
    path('payments/<int:request_id>/rent-request/status/', views.RentRequestStatusView.as_view(), name='rent-request-status'),
    path('payments/rent-request/status-choices/', views.RentRequestStatusChoicesView.as_view(), name='rent-request-status-choices'),
    
    # Financial logs endpoint
    path('financialLogs/', views.FinancialLogsView.as_view(), name='financial-logs'),
    
    # QuickBooks endpoints
    path('quickbooks/status/', views.QuickBooksStatusView.as_view(), name='quickbooks-status'),
    path('quickbooks/connect/', views.QuickBooksConnectView.as_view(), name='quickbooks-connect'),
    path('quickbooks/accounts/', views.QuickBooksAccountsView.as_view(), name='quickbooks-accounts'),
    path('quickbooks/journalEntries/', views.QuickBooksJournalEntriesView.as_view(), name='quickbooks-journal-entries'),
    path('property/<int:user_id>/properties/', views.UserPropertiesView.as_view()),
    path('property-by-owner/<int:user_id>/properties/', views.UserPropertiesByOwnerIdView.as_view()),
    # API documentation
    path('docs/', docs_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', docs_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Main URL patterns
urlpatterns = [
    path('', include(api_urlpatterns)),]
