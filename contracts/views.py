from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.core.files.base import ContentFile
import base64
import uuid

from .models import Contract, ContractReminder
from .serializers import (
    ContractSerializer, ContractSendSerializer,
    ContractSignSerializer, ContractRemindSerializer, ContractReminderSerializer
)

class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Handle schema generation for Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Contract.objects.none()
            
        # Only show contracts created by the current user
        return Contract.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        contract = self.get_object()
        if contract.status != 'draft':
            return Response(
                {"error": "Only draft contracts can be sent for signature"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ContractSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set expiration date if provided
        if 'expiration_days' in serializer.validated_data:
            contract.expiration_date = timezone.now() + timezone.timedelta(
                days=serializer.validated_data['expiration_days']
            )
        
        # Send the contract (placeholder for actual sending logic)
        contract.send_for_signature()
        
        # TODO: Send email with signature link
        
        return Response(
            {"status": "Contract sent for signature"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def signed(self, request, pk=None):
        contract = self.get_object()
        if not contract.signed_document:
            return Response(
                {"error": "No signed document available"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # In a real implementation, you would serve the file for download
        return Response({"signed_document_url": contract.signed_document.url})

    @action(detail=True, methods=['post'])
    def remind(self, request, pk=None):
        contract = self.get_object()
        if contract.status != 'sent':
            return Response(
                {"error": "Can only send reminders for contracts that have been sent"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ContractRemindSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create a reminder record
        reminder = ContractReminder.objects.create(
            contract=contract,
            sent_by=request.user,
            notes=serializer.validated_data.get('message', '')
        )
        
        # TODO: Send actual reminder email
        
        return Response(
            {"status": "Reminder sent"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def sign(self, request, pk=None):
        contract = self.get_object()
        if contract.status != 'sent':
            return Response(
                {"error": "Only contracts that have been sent can be signed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ContractSignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # In a real implementation, you would process the signature data
        # and generate a signed PDF. For now, we'll just mark it as signed.
        
        # Generate a simple signed document (in a real app, this would be a proper PDF)
        signed_content = f"SIGNED CONTRACT\n{contract.title}\n\n"
        signed_content += f"Signed by: {serializer.validated_data['signer_name']}\n"
        signed_content += f"Signature: {serializer.validated_data['signature_data'][:50]}...\n"
        signed_content += f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Save the signed document
        filename = f"signed_contract_{contract.id}_{uuid.uuid4().hex[:8]}.txt"
        contract.signed_document.save(
            filename,
            ContentFile(signed_content.encode('utf-8')),
            save=False
        )
        
        # Mark the contract as signed
        contract.mark_as_signed()
        
        return Response(
            {"status": "Contract signed successfully"},
            status=status.HTTP_200_OK
        )
