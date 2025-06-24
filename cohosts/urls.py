from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

app_name = 'cohosts'

# Schema view for Swagger/OpenAPI
docs_schema_view = get_schema_view(
    openapi.Info(
        title="Co-Hosts API",
        default_version='v1',
        description="API for managing property co-hosts",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@inorental.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'cohosts', views.CoHostViewSet, basename='cohost')

# API URL patterns
api_urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Endpoint for listing properties where the current user is a co-host
    path('my-cohosted-properties/', 
         views.CoHostViewSet.as_view({'get': 'my_cohosted_properties'}), 
         name='my-cohosted-properties'),
    
    # API documentation
    path('docs/', docs_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', docs_schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Main URL patterns
urlpatterns = [
    path('', include(api_urlpatterns)),
]