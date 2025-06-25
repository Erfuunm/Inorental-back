from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model as auth_get_user_model
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import CreateAPIView
import stripe
from atlassian import Jira
from djstripe.models import Customer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.decorators import action
# Import permissions first to avoid circular imports
from .permissions import IsAdminOrReadOnly, IsHostOrReadOnly

# Import models
from .models import (
    Property, Amenity, PropertyAmenity, Facility, PropertyFacility,
    HouseRule, PropertyHouseRule, Booking, Review, Conversation,
    ConversationParticipant, Message, Photo, Availability
)

# Import serializers
from .serializers import (
    UserSerializer, PropertySerializer, AmenitySerializer, PropertyAmenitySerializer,
    FacilitySerializer, PropertyFacilitySerializer, HouseRuleSerializer,
    PropertyHouseRuleSerializer, BookingSerializer, ReviewSerializer,
    ConversationSerializer, ConversationParticipantSerializer, MessageSerializer,
    PhotoSerializer, AvailabilitySerializer, CreateBookingSerializer
)

# Get the user model
User = auth_get_user_model()
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class AvailabilityViewSet(viewsets.ModelViewSet):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(property_id=self.request.data.get('property'))

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(property_id=self.request.data.get('property'))

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(self.request.data['password'])
        user.save()

class UserLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer = TokenObtainPairSerializer
    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

        return Response(serializer.validated_data)

class UserLogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        # For JWT, logging out typically means invalidating the token on the client side.
        # If you want to blacklist tokens, you'd implement that here.
        # For now, we'll just return a success message.
        logout(request) # This logs out the Django session, which might still be active.
        return Response({'message': 'Successfully logged out.'})

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()

        queryset = Property.objects.all()
        if self.request.user.is_authenticated:
            # If user is requesting their own properties
            if self.request.query_params.get('my_properties') == 'true':
                queryset = queryset.filter(host=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

class HostPropertyViewSet(PropertyViewSet):
    def get_queryset(self):
        self.queryset = self.queryset.filter(host=self.request.user).all()
        return super().get_queryset()

class AmenityViewSet(viewsets.ModelViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = (IsAdminOrReadOnly,) # Only admin can manage amenities

class PropertyAmenityViewSet(viewsets.ModelViewSet):
    queryset = PropertyAmenity.objects.all()
    serializer_class = PropertyAmenitySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = (IsAdminOrReadOnly,) # Only admin can manage facilities

class PropertyFacilityViewSet(viewsets.ModelViewSet):
    queryset = PropertyFacility.objects.all()
    serializer_class = PropertyFacilitySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class HouseRuleViewSet(viewsets.ModelViewSet):
    queryset = HouseRule.objects.all()
    serializer_class = HouseRuleSerializer
    permission_classes = (IsAdminOrReadOnly,) # Only admin can manage house rules

class PropertyHouseRuleViewSet(viewsets.ModelViewSet):
    queryset = PropertyHouseRule.objects.all()
    serializer_class = PropertyHouseRuleSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
            
        if not self.request.user.is_authenticated:
            return Booking.objects.none()
            
        if self.request.user.is_staff: # Admin can see all bookings
            return Booking.objects.all()
            
        return Booking.objects.filter(guest=self.request.user) | \
               Booking.objects.filter(property__host=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create_booking':
            return CreateBookingSerializer
        return BookingSerializer

    @action(detail=False, methods=['post'])
    def create_booking(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create booking with validated data
        booking = Booking.objects.create(
            guest=request.user,
            property=serializer.validated_data['property'],
            check_in_date=serializer.validated_data['check_in_date'],
            check_out_date=serializer.validated_data['check_out_date'],
            num_guests=serializer.validated_data['num_guests'],
            total_price=serializer.validated_data['total_price'],
            status='pending'
        )

        # Return the created booking using the main serializer
        response_serializer = BookingSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def payment(self, request, pk=None):
        booking = Booking.objects.get(pk=pk)
        amount = int((booking.check_out_date - booking.check_in_date).days * booking.property.price_per_night * 100)
        customer, created = Customer.get_or_create(subscriber=request.user)
        session = stripe.checkout.Session.create(
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount,
                    'product_data': {
                        'name': 'Rental Price',
                        'description': 'Total Price of Rental',
                        'images': ["https://gitlab.canadacentral.cloudapp.azure.com/inorental-backend/media/inorental.png"],
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=self.reverse_action("payment-confirm", args=[booking.booking_id]),
            cancel_url=self.reverse_action("payment-cancle", args=[booking.booking_id]),
        )
        booking.payment_session = session.id
        booking.save()
        return Response({"url": session.url}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], name="booking-payment-confirm", permission_classes=[IsAdminOrReadOnly])
    def payment_confirm(self, request, pk=None):
        booking = Booking.objects.get(pk=pk)
        checkout_session = stripe.checkout.Session.retrieve(
            booking.payment_session,
            expand=['line_items'],
        )
        if checkout_session.payment_status == 'paid':            
            booking.status = 'paid'
            booking.save()
        return Response({"status": checkout_session.payment_status}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["get"], name="booking-payment-cancle", permission_classes=[IsAdminOrReadOnly])
    def payment_cancle(self, request, pk=None):
        pass

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Handle schema generation for Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Conversation.objects.none()
            
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
            
        # Handle unauthenticated users during schema generation
        if not self.request.user.is_authenticated:
            return Conversation.objects.none()
        return Conversation.objects.filter(conversationparticipant__user=self.request.user).distinct()

class ConversationParticipantViewSet(viewsets.ModelViewSet):
    queryset = ConversationParticipant.objects.all()
    serializer_class = ConversationParticipantSerializer
    permission_classes = (permissions.IsAuthenticated,)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Handle schema generation for Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Message.objects.none()
            
        if not self.request.user.is_authenticated:
            return Message.objects.none()
            
        # Handle unauthenticated users during schema generation
        if not self.request.user.is_authenticated:
            return Message.objects.none()
        # Users can only see messages in conversations they are part of
        return Message.objects.filter(conversation__conversationparticipant__user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()

        queryset = Review.objects.all().select_related('guest', 'property', 'booking')
        
        # Filter by property if property_id is provided
        property_id = self.request.query_params.get('property_id')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        # Filter by user if user_id is provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            # Only allow users to view their own reviews or admins to view any reviews
            if not self.request.user.is_staff and str(self.request.user.id) != str(user_id):
                return Review.objects.none()
            queryset = queryset.filter(guest_id=user_id)
        
        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create_review':
            return CreateReviewSerializer
        return ReviewSerializer

    @action(detail=False, methods=['post'])
    def create_review(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create review with validated data
        review = Review.objects.create(
            guest=request.user,
            property=serializer.validated_data['property'],
            booking=serializer.validated_data['booking'],
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data['comment']
        )

        # Return the created review using the main serializer
        response_serializer = ReviewSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)




class PropertyReviewsView(APIView):
    def get(self, request, property_id):
        reviews = Review.objects.filter(property_id=property_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserReviewsView(APIView):
    def get(self, request, user_id):
        reviews = Review.objects.filter(user_id=user_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
