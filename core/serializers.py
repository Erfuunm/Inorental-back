from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone  # Add this import
from .models import (
    Property, Amenity, PropertyAmenity, Facility, PropertyFacility,
    HouseRule, PropertyHouseRule, Booking, Review, Conversation,
    ConversationParticipant, Message, Photo, Availability
)

'''
should be move to the account app
'''
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'profile_picture_url', 'bio', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at', 'profile_picture_url', 'bio')
        ref_name = 'core.UserSerializer'


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True) # Nested serializer for host
    photos = PhotoSerializer(many=True, read_only=True) # Nested serializer for photos
    availabilities = AvailabilitySerializer(many=True, read_only=True) # Nested serializer for availabilities
    current_booking = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = '__all__'

    def get_current_booking(self, obj):
        # Get current active booking for this property
        current_booking = Booking.objects.filter(
            property=obj,
            check_in_date__lte=timezone.now(),
            check_out_date__gte=timezone.now(),
            status='confirmed'
        ).first()

        if current_booking:
            return {
                'guest_email': current_booking.guest.email,
                'check_in_date': current_booking.check_in_date,
                'check_out_date': current_booking.check_out_date
            }
        return None

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class PropertyAmenitySerializer(serializers.ModelSerializer):
    amenity = AmenitySerializer(read_only=True) # Nested serializer for amenity

    class Meta:
        model = PropertyAmenity
        fields = '__all__'

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'

class PropertyFacilitySerializer(serializers.ModelSerializer):
    facility = FacilitySerializer(read_only=True) # Nested serializer for facility

    class Meta:
        model = PropertyFacility
        fields = '__all__'

class HouseRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseRule
        fields = '__all__'

class PropertyHouseRuleSerializer(serializers.ModelSerializer):
    rule = HouseRuleSerializer(read_only=True) # Nested serializer for house rule

    class Meta:
        model = PropertyHouseRule
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

class CreateBookingSerializer(serializers.ModelSerializer):
    property_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Booking
        fields = ['property_id', 'check_in_date', 'check_out_date', 'num_guests']

    def validate(self, data):
        # Check if property exists
        try:
            property = Property.objects.get(property_id=data['property_id'])
        except Property.DoesNotExist:
            raise serializers.ValidationError({'property_id': 'Property does not exist'})

        # Check if dates are valid
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError({'check_out_date': 'Check-out date must be after check-in date'})

        # Check if property is available for these dates
        overlapping_bookings = Booking.objects.filter(
            property_id=data['property_id'],
            check_in_date__lt=data['check_out_date'],
            check_out_date__gt=data['check_in_date'],
            status='confirmed'
        )
        if overlapping_bookings.exists():
            raise serializers.ValidationError('Property is not available for these dates')

        # Check if number of guests is valid
        if data['num_guests'] > property.max_guests:
            raise serializers.ValidationError({'num_guests': f'Maximum number of guests allowed is {property.max_guests}'})

        # Calculate total price
        days = (data['check_out_date'] - data['check_in_date']).days
        data['total_price'] = property.price_per_night * days
        data['property'] = property

        return data

class ReviewSerializer(serializers.ModelSerializer):
    guest = UserSerializer(read_only=True)
    property = PropertySerializer(read_only=True)
    booking = BookingSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

class CreateReviewSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Review
        fields = ['booking_id', 'rating', 'comment']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')
        return value

    def validate(self, data):
        try:
            booking = Booking.objects.get(booking_id=data['booking_id'])
            
            # Check if the user is the guest of this booking
            if booking.guest != self.context['request'].user:
                raise serializers.ValidationError({'booking_id': 'You can only review your own bookings'})
            
            # Check if the booking is completed
            if booking.status != 'confirmed':
                raise serializers.ValidationError({'booking_id': 'You can only review completed bookings'})
            
            # Check if the checkout date has passed
            if booking.check_out_date > timezone.now().date():
                raise serializers.ValidationError({'booking_id': 'You can only review after your stay'})
            
            # Check if a review already exists
            if Review.objects.filter(booking=booking).exists():
                raise serializers.ValidationError({'booking_id': 'You have already reviewed this booking'})
            
            # Add property to validated data
            data['property'] = booking.property
            data['booking'] = booking
            
            return data
            
        except Booking.DoesNotExist:
            raise serializers.ValidationError({'booking_id': 'Booking does not exist'})

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    booking = BookingSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True) # Nested serializer for messages

    class Meta:
        model = Conversation
        fields = '__all__'

class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ConversationParticipant
        fields = '__all__'

class VisitorTaskSerializer(serializers.Serializer):
    class Meta:
        fields = '__all__'
    subject = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    
