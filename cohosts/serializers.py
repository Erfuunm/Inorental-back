from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_serializer_method
from drf_yasg import openapi

from core.models import Property
from .models import CoHost

User = get_user_model()


class CoHostUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details in co-host responses
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_picture_url']
        read_only_fields = fields


class CoHostPropertySerializer(serializers.ModelSerializer):
    """
    Serializer for property details in co-host responses
    """
    class Meta:
        model = Property
        fields = ['property_id', 'title', 'property_type']
        read_only_fields = fields


class CoHostSerializer(serializers.ModelSerializer):
    """Serializer for CoHost model"""
    user = CoHostUserSerializer(read_only=True)
    property = CoHostPropertySerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
        write_only=True,
        required=True
    )

    class Meta:
        model = CoHost
        fields = [
            'cohost_id', 'user', 'user_id', 'property', 'property_id', 'role',
            'can_manage_bookings', 'can_manage_calendar', 'can_manage_listing',
            'can_manage_finances', 'can_manage_messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        # Check if user is not the property owner
        property = data.get('property')
        user = data.get('user')
        
        if property.host == user:
            raise serializers.ValidationError("Property owner cannot be added as a co-host.")
        
        # Check if user is already a co-host for this property
        if CoHost.objects.filter(property=property, user=user).exists():
            # If updating existing co-host, allow it
            if self.instance and self.instance.user == user and self.instance.property == property:
                return data
            raise serializers.ValidationError("This user is already a co-host for this property.")
        
        return data


class CoHostCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating CoHost instances"""
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True
    )
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
        write_only=True,
        required=True
    )

    class Meta:
        model = CoHost
        fields = [
            'user_id', 'property_id', 'role',
            'can_manage_bookings', 'can_manage_calendar', 'can_manage_listing',
            'can_manage_finances', 'can_manage_messages'
        ]

    def validate(self, data):
        # Check if user is not the property owner
        property = data.get('property')
        user = data.get('user')
        
        if property.host == user:
            raise serializers.ValidationError("Property owner cannot be added as a co-host.")
        
        # Check if user is already a co-host for this property
        if CoHost.objects.filter(property=property, user=user).exists():
            # If updating existing co-host, allow it
            if self.instance and self.instance.user == user and self.instance.property == property:
                return data
            raise serializers.ValidationError("This user is already a co-host for this property.")
        
        return data
