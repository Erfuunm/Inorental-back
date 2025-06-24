from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.functional import cached_property
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.models import Property
from .models import CoHost
from .serializers import CoHostSerializer, CoHostCreateUpdateSerializer
from account.models import User

class CoHostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing co-hosts for properties.
    
    This viewset provides the following actions:
    - list: List all co-hosts for a specific property
    - create: Add a new co-host to a property
    - retrieve: Get details of a specific co-host
    - update: Update a co-host's permissions or role
    - destroy: Remove a co-host from a property
    - my_cohosted_properties: List all properties where the current user is a co-host
    """
    serializer_class = CoHostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the action.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return CoHostCreateUpdateSerializer
        return CoHostSerializer
    
    @cached_property
    def swagger_fake_view(self):
        """
        This is a workaround to prevent Swagger from trying to execute the queryset
        during schema generation.
        """
        return getattr(self, 'swagger_fake_view', False)
    
    def get_queryset(self):
        """
        Return co-hosts for the current user's properties or where the user is a co-host.
        """
        # Skip queryset evaluation during schema generation
        if self.swagger_fake_view:
            return CoHost.objects.none()
            
        # If it's a nested route under a property
        property_id = self.kwargs.get('property_pk')
        if property_id:
            # For property-specific co-hosts, check if user is the owner or a co-host
            property = get_object_or_404(Property, id=property_id)
            if property.host == self.request.user or \
               CoHost.objects.filter(property=property, user=self.request.user).exists():
                return CoHost.objects.filter(property=property)
            return CoHost.objects.none()
        
        # For the general cohosts list, return co-hosts for properties the user owns
        # or where the user is a co-host
        return CoHost.objects.filter(
            Q(property__host=self.request.user) |  # User is property owner
            Q(user=self.request.user)  # User is a co-host
        ).distinct()
    
    def get_property(self):
        """Get the property from the URL parameter"""
        property_id = self.kwargs.get('property_id')
        return get_object_or_404(Property, pk=property_id)
    
    def get_serializer_context(self):
        """Add the request to the serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        """
        List all co-hosts for a property.
        GET /properties/{property_id}/cohosts/
        """
        property = self.get_property()
        
        # Check if the user is the property owner or a co-host
        if not (property.host == request.user or 
                CoHost.objects.filter(property=property, user=request.user).exists()):
            return Response(
                {"detail": "You do not have permission to view co-hosts for this property."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        queryset = self.get_queryset().filter(property=property)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Add a new co-host to a property.
        POST /properties/{property_id}/cohosts/
        """
        property = self.get_property()
        
        # Only the property owner can add co-hosts
        if property.host != request.user:
            return Response(
                {"detail": "You do not have permission to add co-hosts to this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=property)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get details of a specific co-host.
        GET /properties/{property_id}/cohosts/{cohost_id}/
        """
        instance = self.get_object()
        
        # Check if the user has permission to view this co-host
        property = instance.property
        if not (property.host == request.user or 
                CoHost.objects.filter(property=property, user=request.user).exists()):
            return Response(
                {"detail": "You do not have permission to view this co-host."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        Update a co-host's permissions or role.
        PUT /properties/{property_id}/cohosts/{cohost_id}/
        """
        instance = self.get_object()
        property = instance.property
        
        # Only the property owner can update co-host permissions
        if property.host != request.user:
            return Response(
                {"detail": "You do not have permission to update co-host permissions."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Don't allow changing the property or user
        if 'property' in request.data or 'user' in request.data:
            return Response(
                {"detail": "Cannot change the property or user of an existing co-host."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove a co-host from a property.
        DELETE /properties/{property_id}/cohosts/{cohost_id}/
        """
        instance = self.get_object()
        property = instance.property
        
        # Only the property owner can remove co-hosts
        if property.host != request.user:
            return Response(
                {"detail": "You do not have permission to remove co-hosts from this property."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="List all properties where the current user is a co-host",
        responses={
            200: openapi.Response('List of properties where the user is a co-host', 
                               schema=openapi.Schema(
                                   type=openapi.TYPE_ARRAY,
                                   items=openapi.Items(type=openapi.TYPE_OBJECT)
                               )),
            401: 'Authentication credentials were not provided.',
        },
        security=[{"Bearer": []}]
    )
    @action(detail=False, methods=['get'], url_path='my-cohosted-properties')
    def my_cohosted_properties(self, request):
        """
        List all properties where the current user is a co-host.
        """
        cohosted_properties = Property.objects.filter(
            cohosts__user=request.user
        ).distinct()
        
        # Use the PropertySerializer from core app to maintain consistency
        from core.serializers import PropertySerializer
        
        serializer = PropertySerializer(
            properties,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
