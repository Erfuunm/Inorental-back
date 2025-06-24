from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'regulations', views.RegulationViewSet, basename='regulation')
router.register(r'regulation-recipients', views.RegulationRecipientViewSet, basename='regulation-recipient')

urlpatterns = [
    path('', include(router.urls)),
]
