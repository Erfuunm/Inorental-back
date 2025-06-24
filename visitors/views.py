from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import Visitor, Visit
from .serializers import VisitorSerializer, VisitSerializer
from core.permissions import IsAdminOrReadOnly


class VisitorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing visitors.
    """
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter visitors by status, search term, or show only those needing follow-up.
        """
        queryset = Visitor.objects.all()
        
        # Filter by status if provided
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        # Search by name or email if search term provided
        search_term = self.request.query_params.get('search', None)
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) |
                Q(last_name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone__icontains=search_term)
            )
            
        # Filter visitors with upcoming follow-ups if needed
        needs_follow_up = self.request.query_params.get('needs_follow_up', None)
        if needs_follow_up and needs_follow_up.lower() == 'true':
            queryset = queryset.filter(
                visits__follow_up_required=True,
                visits__follow_up_date__isnull=False,
                visits__follow_up_date__gte=timezone.now()
            ).distinct()
            
        return queryset.order_by('-last_visit_date', '-created_at')
    
    def perform_create(self, serializer):
        """Set the created_by field to the current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def visits(self, request, pk=None):
        """Get all visits for a specific visitor."""
        visitor = self.get_object()
        visits = visitor.visits.all().order_by('-visit_date')
        serializer = VisitSerializer(visits, many=True, context={'request': request})
        return Response(serializer.data)


class VisitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing visits.
    """
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally filter visits by visitor, property, or upcoming follow-ups.
        """
        queryset = Visit.objects.all()
        
        # Filter by visitor if provided
        visitor_id = self.request.query_params.get('visitor', None)
        if visitor_id:
            queryset = queryset.filter(visitor_id=visitor_id)
            
        # Filter by property if provided
        property_id = self.request.query_params.get('property', None)
        if property_id:
            queryset = queryset.filter(property_id=property_id)
            
        # Filter by assigned user if provided
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            if assigned_to == 'me':
                queryset = queryset.filter(assigned_to=self.request.user)
            else:
                queryset = queryset.filter(assigned_to_id=assigned_to)
                
        # Filter by follow-up required
        follow_up_required = self.request.query_params.get('follow_up_required', None)
        if follow_up_required:
            if follow_up_required.lower() == 'true':
                queryset = queryset.filter(follow_up_required=True)
            elif follow_up_required.lower() == 'false':
                queryset = queryset.filter(follow_up_required=False)
                
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(visit_date__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(visit_date__date__lte=end_date)
            
        # Filter upcoming follow-ups
        upcoming_follow_ups = self.request.query_params.get('upcoming_follow_ups', None)
        if upcoming_follow_ups and upcoming_follow_ups.lower() == 'true':
            queryset = queryset.filter(
                follow_up_required=True,
                follow_up_date__isnull=False,
                follow_up_date__gte=timezone.now()
            )
            
        return queryset.order_by('-visit_date')
    
    def perform_create(self, serializer):
        """Set the assigned_to field to the current user if not provided."""
        if 'assigned_to' not in serializer.validated_data:
            serializer.save(assigned_to=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def complete_follow_up(self, request, pk=None):
        """Mark a follow-up as completed."""
        visit = self.get_object()
        
        if not visit.follow_up_required:
            return Response(
                {'detail': 'This visit does not require follow-up.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        visit.follow_up_required = False
        visit.follow_up_notes = request.data.get('follow_up_notes', visit.follow_up_notes)
        visit.save()
        
        serializer = self.get_serializer(visit)
        return Response(serializer.data)
