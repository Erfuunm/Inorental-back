from rest_framework import serializers
from .models import Regulation, RegulationRecipient, DocumentType, RegulationStatus
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'email', 'first_name', 'last_name']
        ref_name = 'regulations.UserSerializer'

class RegulationRecipientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    
    class Meta:
        model = RegulationRecipient
        fields = ['id', 'user', 'user_id', 'sent_at', 'viewed_at', 'acknowledged', 'acknowledged_at']
        read_only_fields = ['id', 'sent_at', 'viewed_at', 'acknowledged_at']

class RegulationSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by = UserSerializer(read_only=True)
    recipients = RegulationRecipientSerializer(many=True, read_only=True)
    
    class Meta:
        model = Regulation
        fields = [
            'id', 'title', 'description', 'document', 'document_url',
            'document_type', 'document_type_display', 'status', 'status_display',
            'effective_date', 'expiration_date', 'property', 'created_by',
            'created_at', 'updated_at', 'recipients'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
        extra_kwargs = {
            'document': {'write_only': True},
        }
    
    def get_document_url(self, obj):
        if obj.document:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.document.url)
            return obj.document.url
        return None
    
    def validate(self, data):
        effective_date = data.get('effective_date')
        expiration_date = data.get('expiration_date')
        
        if expiration_date and effective_date and expiration_date < effective_date:
            raise serializers.ValidationError({
                'expiration_date': 'Expiration date must be after effective date.'
            })
            
        return data

class RegulationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulation
        fields = [
            'title', 'description', 'document', 'document_type', 'status',
            'effective_date', 'expiration_date', 'property'
        ]
        extra_kwargs = {
            'document': {'required': True}
        }

class SendRegulationSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        required=True,
        min_length=1
    )
    message = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        # This is just a serializer for validation, not for creating objects
        return validated_data
