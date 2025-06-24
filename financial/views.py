from rest_framework import status, filters, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)
from rest_framework.permissions import IsAuthenticated, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, JsonResponse
import os
from django.conf import settings
from core.models import Property
from .models import Payment, RentRequest
from .serializers import (
    PaymentSerializer,
    PaymentSyncSerializer,
    QuickBooksAccountSerializer,
    JournalEntrySerializer
)
from datetime import timedelta
from django.utils import timezone


class UserPropertiesView(APIView):
    """
    get:
    Returns a list of all properties a user has put up for rent (hosted).
    - **user_id**: The user id (host) whose properties you want to see.
    - **Response**: List of property objects.
    """
    def get(self, request, user_id):
        properties = Property.objects.filter(host_id=user_id)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

class UserPropertiesByOwnerIdView(APIView):
    """
    get:
    Returns a list of all properties where owner_id matches the user_id (legacy/alternate endpoint).
    - **user_id**: The owner id whose properties you want to see.
    - **Response**: List of property objects.
    """
    def get(self, request, user_id):
        properties = Property.objects.filter(owner_id=user_id)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data)

class RentRequestStatusChoicesView(APIView):
    """
    get:
    Returns all possible status choices for a rent request.
    - **Response**: List of status values and their display names.
    """
    def get(self, request):
        from .models import RentRequest
        choices = [
            {"value": choice[0], "display": choice[1]}
            for choice in RentRequest.StatusChoices.choices
        ]
        return Response(choices)

class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class PaymentListCreateView(ListCreateAPIView):
    """
    API endpoint to list all payments or create a new payment.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = {
        'status': ['exact'],
        'payment_method': ['exact'],
        'payment_category': ['exact'],
        'created_at': ['date__gte', 'date__lte', 'exact'],
        'amount': ['gte', 'lte', 'exact'],
    }
    search_fields = ['transaction_id', 'payer_id', 'property_id', 'notes']
    ordering_fields = ['created_at', 'amount', 'updated_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PaymentRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    API endpoint to retrieve, update or delete a payment.
    Only admin users can update or delete payments.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class SyncPaymentsView(APIView):
    """
    API endpoint to sync payments with QuickBooks.
    Currently, this just marks payments as synced.
    In the future, this will integrate with QuickBooks API.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PaymentSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_ids = serializer.validated_data['payment_ids']
        updated = Payment.objects.filter(
            id__in=payment_ids,
            synced_to_quickbooks=False
        ).update(
            synced_to_quickbooks=True,
            quickbooks_ref=f"QB-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        return Response({
            'message': f'Successfully synced {updated} payments to QuickBooks',
            'synced_count': updated
        })


class FinancialLogsView(ListAPIView):
    """
    API endpoint to retrieve financial transaction logs.
    This can be extended to include more detailed logging in the future.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'payment_method': ['exact'],
        'created_at': ['date__gte', 'date__lte', 'exact'],
    }
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_queryset(self):
        # In a real implementation, you might want to include more than just payments
        return Payment.objects.all()


class QuickBooksStatusView(APIView):
    """
    API endpoint to check QuickBooks connection status.
    Currently returns a mock response.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Implement actual QuickBooks connection check
        return Response({
            'connected': False,
            'last_sync': None,
            'quickbooks_online': False,
            'message': 'QuickBooks integration is not yet implemented. Currently using mock data.'
        })


class QuickBooksConnectView(APIView):
    """
    API endpoint to initiate OAuth connection with QuickBooks.
    Currently a placeholder for future implementation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # TODO: Implement actual QuickBooks OAuth flow
        return Response({
            'status': 'not_implemented',
            'message': 'QuickBooks OAuth integration is not yet implemented.'
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class QuickBooksAccountsView(APIView):
    """
    API endpoint to list accounts from QuickBooks chart.
    Currently returns mock data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: Replace with actual QuickBooks API call
        mock_accounts = [
            {
                'id': '1',
                'name': 'Accounts Receivable',
                'account_type': 'Accounts Receivable',
                'account_sub_type': 'AccountsReceivable',
                'currency': 'USD',
                'active': True
            },
            {
                'id': '2',
                'name': 'Bank Account',
                'account_type': 'Bank',
                'account_sub_type': 'Checking',
                'currency': 'USD',
                'active': True
            }
        ]
        serializer = QuickBooksAccountSerializer(mock_accounts, many=True)
        return Response(serializer.data)


class QuickBooksJournalEntriesView(APIView):
    """
    API endpoint to create manual journal entries in QuickBooks.
    Currently a placeholder for future implementation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JournalEntrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implement actual QuickBooks journal entry creation
        return Response({
            'status': 'not_implemented',
            'message': 'QuickBooks journal entry creation is not yet implemented.',
            'data': serializer.validated_data
        }, status=status.HTTP_501_NOT_IMPLEMENTED)


class DownloadFinancialRecordsView(APIView):
    """
    API endpoint to download the financial records Excel file.
    Only accessible by admin users.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        excel_file_path = os.path.join(settings.BASE_DIR, 'financial_records.xlsx')
        
        if not os.path.exists(excel_file_path):
            return Response(
                {'error': 'Financial records file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            response = FileResponse(
                open(excel_file_path, 'rb'),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=financial_records.xlsx'
            return response
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RentRequestStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, request_id):
        try:
            rent_request = RentRequest.objects.get(id=request_id, user=request.user)
        except RentRequest.DoesNotExist:
            return Response({'error': 'Rent request not found'}, status=status.HTTP_404_NOT_FOUND)
        cancel_deadline = rent_request.created_at + timedelta(hours=24)
        status_data = {
            "status": rent_request.status,
            "cancel_deadline": cancel_deadline,
            "can_cancel": timezone.now() < cancel_deadline and rent_request.status == 'pending',
        }
        return Response(status_data)
