from django.db import models
from django.conf import settings
from core.models import Property


class CoHost(models.Model):
    """
    Model to manage co-hosts for properties.
    """
    class Role(models.TextChoices):
        COHOST = 'cohost', 'Co-Host'
        MANAGER = 'manager', 'Property Manager'
        CLEANER = 'cleaner', 'Cleaning Staff'
        MAINTENANCE = 'maintenance', 'Maintenance Staff'

    id = models.AutoField(primary_key=True, verbose_name='ID')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='cohosts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cohosted_properties')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.COHOST)
    can_manage_bookings = models.BooleanField(default=False, verbose_name='Can manage bookings')
    can_manage_calendar = models.BooleanField(default=False, verbose_name='Can manage calendar')
    can_manage_listing = models.BooleanField(default=False, verbose_name='Can manage listing')
    can_manage_finances = models.BooleanField(default=False, verbose_name='Can manage finances')
    can_manage_messages = models.BooleanField(default=False, verbose_name='Can manage messages')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        unique_together = ('property', 'user')
        verbose_name = 'Co-Host'
        verbose_name_plural = 'Co-Hosts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} as {self.get_role_display()} for {self.property.title}"
    
    def has_permission(self, permission_type):
        """Check if co-host has a specific permission"""
        permission_map = {
            'manage_bookings': self.can_manage_bookings,
            'manage_calendar': self.can_manage_calendar,
            'manage_listing': self.can_manage_listing,
            'manage_finances': self.can_manage_finances,
            'manage_messages': self.can_manage_messages,
        }
        return permission_map.get(permission_type, False)
