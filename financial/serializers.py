from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'transaction_id',
            'created_at',
            'amount',
            'currency',
            'status',
            'status_display',
            'payment_method',
            'payment_method_display',
            'payer_id',
            'property_id',
            'payment_category',
            'notes',
            'synced_to_quickbooks',
            'quickbooks_ref',
            'created_by',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'synced_to_quickbooks', 'quickbooks_ref']

    def create(self, validated_data):
        # Set the created_by user to the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PaymentSyncSerializer(serializers.Serializer):
    payment_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of payment IDs to sync with QuickBooks"
    )


class QuickBooksAccountSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    account_type = serializers.CharField()
    account_sub_type = serializers.CharField()
    currency = serializers.CharField()
    active = serializers.BooleanField()


class JournalEntrySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    description = serializers.CharField(required=True)
    line_items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        min_length=2
    )
