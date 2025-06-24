from django.db import models
from django.conf import settings
from django.utils import timezone

class Visitor(models.Model):
    """
    Model to store information about visitors.
    """
    VISITOR_STATUS_CHOICES = [
        ('new', 'New'),
        ('returning', 'Returning'),
        ('converted', 'Converted to Customer'),
        ('lost', 'Lost'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=VISITOR_STATUS_CHOICES, 
        default='new'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_visitors'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_visit_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-last_visit_date', '-created_at']
        verbose_name = 'Visitor'
        verbose_name_plural = 'Visitors'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def update_last_visit(self):
        """Update the last visit timestamp"""
        self.last_visit_date = timezone.now()
        self.save(update_fields=['last_visit_date'])


class Visit(models.Model):
    """
    Model to track each visit made by a visitor.
    """
    VISIT_PURPOSE_CHOICES = [
        ('property_viewing', 'Property Viewing'),
        ('inquiry', 'General Inquiry'),
        ('follow_up', 'Follow-up Visit'),
        ('other', 'Other'),
    ]
    
    visitor = models.ForeignKey(
        Visitor, 
        on_delete=models.CASCADE, 
        related_name='visits'
    )
    visit_date = models.DateTimeField(default=timezone.now)
    purpose = models.CharField(
        max_length=20, 
        choices=VISIT_PURPOSE_CHOICES, 
        default='property_viewing'
    )
    property = models.ForeignKey(
        'core.Property', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='visits'
    )
    notes = models.TextField(blank=True, null=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    follow_up_notes = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_visits'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date']
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'
    
    def __str__(self):
        return f"Visit by {self.visitor} on {self.visit_date.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Update the visitor's last_visit_date when a new visit is created
        if not self.pk:  # Only for new instances
            self.visitor.update_last_visit()
        super().save(*args, **kwargs)
