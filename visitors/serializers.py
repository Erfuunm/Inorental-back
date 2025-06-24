from rest_framework import serializers
from .models import Visitor, Visit
from core.serializers import PropertySerializer, UserSerializer

class VisitorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Visitor model.
    """
    created_by_details = UserSerializer(source='created_by', read_only=True)
    visit_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 
            'address', 'notes', 'status', 'created_by', 'created_by_details',
            'created_at', 'updated_at', 'last_visit_date', 'visit_count'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'last_visit_date', 'visit_count')
        extra_kwargs = {
            'created_by': {'write_only': True}
        }
    
    def get_visit_count(self, obj):
        """Get the count of visits for this visitor."""
        return obj.visits.count()
    
    def create(self, validated_data):
        """Create a new visitor."""
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class VisitSerializer(serializers.ModelSerializer):
    """
    Serializer for the Visit model.
    """
    visitor_details = VisitorSerializer(source='visitor', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = Visit
        fields = [
            'id', 'visitor', 'visitor_details', 'visit_date', 'purpose',
            'property', 'property_details', 'notes', 'follow_up_required',
            'follow_up_date', 'follow_up_notes', 'assigned_to', 'assigned_to_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at')
        extra_kwargs = {
            'visitor': {'write_only': True},
            'property': {'write_only': True},
            'assigned_to': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create a new visit."""
        # If assigned_to is not provided, default to the current user
        if 'assigned_to' not in validated_data:
            validated_data['assigned_to'] = self.context['request'].user
        return super().create(validated_data)
