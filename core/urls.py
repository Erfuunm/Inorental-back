from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router
router = DefaultRouter()

# Import views inside the function to avoid circular imports
def get_urlpatterns():
    from .views import (
        UserRegistrationView, UserLoginView, UserLogoutView, UserProfileView,
        PropertyViewSet, HostPropertyViewSet, AmenityViewSet, PropertyAmenityViewSet, FacilityViewSet,
        PropertyFacilityViewSet, HouseRuleViewSet, PropertyHouseRuleViewSet,
        BookingViewSet, ReviewViewSet, ConversationViewSet, ConversationParticipantViewSet,
        MessageViewSet, PhotoViewSet, AvailabilityViewSet
    )
    
    # Register viewsets with the router
    router.register(r'properties', PropertyViewSet)
    router.register(r'host-properties', HostPropertyViewSet)
    
    router.register(r'amenities', AmenityViewSet)
    router.register(r'property-amenities', PropertyAmenityViewSet)
    router.register(r'facilities', FacilityViewSet)
    router.register(r'property-facilities', PropertyFacilityViewSet)
    router.register(r'house-rules', HouseRuleViewSet)
    router.register(r'property-house-rules', PropertyHouseRuleViewSet)
    router.register(r'bookings', BookingViewSet)
    router.register(r'reviews', ReviewViewSet)
    router.register(r'conversations', ConversationViewSet)
    router.register(r'conversation-participants', ConversationParticipantViewSet)
    router.register(r'messages', MessageViewSet)
    router.register(r'photos', PhotoViewSet)
    router.register(r'availabilities', AvailabilityViewSet)
    
    urlpatterns = [
        path('register/', UserRegistrationView.as_view(), name='user-register'),
        path('login/', UserLoginView.as_view(), name='user-login'),
        path('logout/', UserLogoutView.as_view(), name='user-logout'),
        path('profile/', UserProfileView.as_view(), name='user-profile'),
        path('', include(router.urls)),
        path('properties/<int:property_id>/reviewsbyproperty/', views.PropertyReviewsView.as_view(), name='property-reviews'),
        path('properties/<int:user_id>/reviewsbyuser/', views.UserReviewsView.as_view(), name='user-reviews'),
    ]
    
    return urlpatterns

# Call the function to get the URL patterns
urlpatterns = get_urlpatterns()
