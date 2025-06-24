from rest_framework import serializers
from .models import Contract, ContractReminder
from django.utils import timezone

class ContractReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractReminder
        fields = ['id', 'sent_at', 'sent_by', 'notes']
        read_only_fields = ['sent_at', 'sent_by']

class ContractSerializer(serializers.ModelSerializer):
    reminders = ContractReminderSerializer(many=True, read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'title', 'content', 'customer_name', 'customer_email',
            'customer_phone', 'customer_number', 'status', 'created_at',
            'updated_at', 'sent_at', 'signed_at', 'signed_document',
            'expiration_date', 'is_expired', 'reminders'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sent_at', 'signed_at', 'status']
    
    def get_is_expired(self, obj):
        return obj.is_expired()

class ContractSendSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
    expiration_days = serializers.IntegerField(min_value=1, default=7)

class ContractSignSerializer(serializers.Serializer):
    signature_data = serializers.CharField(required=True)
    signer_name = serializers.CharField(required=True)

class ContractRemindSerializer(serializers.Serializer):
    message = serializers.CharField(required=False, allow_blank=True)
