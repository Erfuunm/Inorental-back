"""
URL configuration for inorental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Contracts API",
        default_version='v1',
        description="""
        API documentation for the Inorental project.
        This includes both core functionality and financial management.
        
        Available endpoints:
        - /api/ - Core API endpoints
        - /api/financial/ - Financial management endpoints
        - /api/token/ - JWT token authentication
        - /api/token/refresh/ - JWT token refresh
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    urlconf='inorental.urls',
    authentication_classes=[]
)

urlpatterns = [
    # Admin
    path(settings.BASE_URL + "admin/", admin.site.urls),
    
    # API endpoints
    path(settings.BASE_URL +  "api/", include("core.urls")),
    path(settings.BASE_URL + "api/", include("visitors.urls")),  # Include visitors app URLs
    path(settings.BASE_URL +  "api/financial/", include("financial.urls")),  # Financial app URLs
    path(settings.BASE_URL + "api/", include("core.urls")),
    
    path(settings.BASE_URL +"api/", include("cohosts.urls")),

    path(settings.BASE_URL + "api/", include("visitors.urls")),  # Include visitors app URLs
    path(settings.BASE_URL + "api/", include("contacts.urls")),  # Include contacts app URLs
    path(settings.BASE_URL + "api/", include("contracts.urls")),  # Include contracts app URLs
    path(settings.BASE_URL + "api/", include("regulations.urls")),  # Include regulations app URLs
    path(settings.BASE_URL + 'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(settings.BASE_URL +  'api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(settings.BASE_URL +  "api/", include("visitors.urls")),
    # API Documentation
    path(settings.BASE_URL + 'swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(settings.BASE_URL + 'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(settings.BASE_URL +  'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Root URL
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(settings.BASE_URL + 'redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
