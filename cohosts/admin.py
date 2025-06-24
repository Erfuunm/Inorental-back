from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode
from .models import CoHost


@admin.register(CoHost)
class CoHostAdmin(admin.ModelAdmin):
    """
    Admin interface for managing CoHost instances.
    """
    list_display = (
        'get_user_email',
        'get_property_title',
        'role',
        'get_permissions_display',
        'created_at',
    )
    list_filter = (
        'role',
        'can_manage_bookings',
        'can_manage_calendar',
        'can_manage_listing',
        'can_manage_finances',
        'can_manage_messages',
        'created_at',
    )
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
        'property__title',
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Co-Host Information', {
            'fields': ('user', 'property', 'role')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_bookings',
                'can_manage_calendar',
                'can_manage_listing',
                'can_manage_finances',
                'can_manage_messages',
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize database queries by selecting related fields"""
        return super().get_queryset(request).select_related('user', 'property')
    
    def get_user_email(self, obj):
        """Display user email with link to user admin"""
        url = reverse('admin:account_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    get_user_email.short_description = 'User'
    get_user_email.admin_order_field = 'user__email'
    
    def get_property_title(self, obj):
        """Display property title with link to property admin"""
        url = reverse('admin:core_property_change', args=[obj.property.id])
        return format_html('<a href="{}">{}</a>', url, obj.property.title)
    get_property_title.short_description = 'Property'
    get_property_title.admin_order_field = 'property__title'
    
    def get_permissions_display(self, obj):
        """Display a comma-separated list of permissions"""
        permissions = []
        if obj.can_manage_bookings:
            permissions.append('Bookings')
        if obj.can_manage_calendar:
            permissions.append('Calendar')
        if obj.can_manage_listing:
            permissions.append('Listing')
        if obj.can_manage_finances:
            permissions.append('Finances')
        if obj.can_manage_messages:
            permissions.append('Messages')
        return ', '.join(permissions) if permissions else 'None'
    get_permissions_display.short_description = 'Permissions'
