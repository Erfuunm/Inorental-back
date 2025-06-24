"""
Signal handlers for the cohosts app.
"""
from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import CoHost


@receiver(pre_save, sender=CoHost)
def validate_cohost(sender, instance, **kwargs):
    """
    Validate co-host before saving.
    """
    # Ensure the user is not the property owner
    if instance.user == instance.property.host:
        raise ValidationError("Property owner cannot be added as a co-host.")
    
    # Check for duplicate co-host entries
    if CoHost.objects.filter(property=instance.property, user=instance.user).exclude(pk=instance.pk).exists():
        raise ValidationError("This user is already a co-host for this property.")


@receiver(post_save, sender=CoHost)
def cohost_created_or_updated(sender, instance, created, **kwargs):
    """
    Handle post-save actions for CoHost model.
    """
    if created:
        # Send notification to the new co-host
        pass  # Add notification logic here
    else:
        # Handle co-host update
        pass  # Add update logic here


@receiver(pre_delete, sender=CoHost)
def cohost_pre_delete(sender, instance, **kwargs):
    """
    Handle pre-delete actions for CoHost model.
    """
    # Add any pre-delete logic here
    pass


@receiver(post_delete, sender=CoHost)
def cohost_post_delete(sender, instance, **kwargs):
    """
    Handle post-delete actions for CoHost model.
    """
    # Send notification to the co-host that they've been removed
    pass  # Add notification logic here
