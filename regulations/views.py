import os
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import status, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Regulation, RegulationRecipient, RegulationStatus
from .serializers import (
    RegulationSerializer, RegulationCreateSerializer,
    SendRegulationSerializer, RegulationRecipientSerializer
)
from core.permissions import IsAdminOrReadOnly

class RegulationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint for managing regulations.
    """
    queryset = Regulation.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegulationCreateSerializer
        return RegulationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by property if provided
        property_id = self.request.query_params.get('property_id')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        # Filter by document type if provided
        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        # Filter by status if provided, default to published only for non-staff
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        elif not self.request.user.is_staff:
            queryset = queryset.filter(status=RegulationStatus.PUBLISHED)
        
        return queryset.select_related('created_by', 'property')

    def perform_create(self, serializer):
        # Set the created_by field to the current user
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download the regulation document."""
        regulation = self.get_object()
        if not regulation.document:
            return Response(
                {'detail': 'No document found for this regulation.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            response = FileResponse(regulation.document.open('rb'))
            filename = os.path.basename(regulation.document.name)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except FileNotFoundError:
            raise Http404("The requested file does not exist.")

    @action(detail=True, methods=['post'], serializer_class=SendRegulationSerializer)
    def send(self, request, pk=None):
        """Send the regulation to specified users."""
        regulation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_ids = [user.id for user in serializer.validated_data['user_ids']]
        message = serializer.validated_data.get('message', '')
        
        # Create or update regulation recipients
        recipients = []
        for user_id in user_ids:
            recipient, created = RegulationRecipient.objects.get_or_create(
                regulation=regulation,
                user_id=user_id,
                defaults={'sent_at': timezone.now()}
            )
            if not created:
                recipient.sent_at = timezone.now()
                recipient.save()
            recipients.append(recipient)
        
        # TODO: Send notification/email to users with the regulation
        # This would involve integrating with your notification system
        
        # Return the list of recipients
        recipient_serializer = RegulationRecipientSerializer(
            recipients, many=True, context={'request': request}
        )
        return Response(recipient_serializer.data, status=status.HTTP_200_OK)

class RegulationRecipientViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint for managing regulation recipients.
    """
    serializer_class = RegulationRecipientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Regular users can only see their own received regulations
        queryset = RegulationRecipient.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset.select_related('user', 'regulation')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge receipt of a regulation."""
        recipient = self.get_object()
        
        # Only the recipient can acknowledge
        if recipient.user != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        recipient.acknowledged = True
        recipient.acknowledged_at = timezone.now()
        recipient.viewed_at = timezone.now()
        recipient.save()
        
        serializer = self.get_serializer(recipient)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Mark a regulation as viewed by the recipient."""
        recipient = self.get_object()
        
        # Only the recipient can mark as viewed
        if recipient.user != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not recipient.viewed_at:
            recipient.viewed_at = timezone.now()
            recipient.save()
        
        serializer = self.get_serializer(recipient)
        return Response(serializer.data)
