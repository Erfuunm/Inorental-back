from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from enum import Enum
import os

class DocumentType(models.TextChoices):
    BUILDING_REGULATIONS = 'building', 'Building Regulations'
    COMMUNITY_GUIDELINES = 'community', 'Community Guidelines'
    HOUSE_RULES = 'house_rules', 'House Rules'
    OTHER = 'other', 'Other'

class RegulationStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'

def regulation_document_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/regulations/<id>/<filename>
    return f'regulations/{instance.id}/{filename}'

class Regulation(models.Model):
    """Model to store regulation documents."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document = models.FileField(
        upload_to=regulation_document_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'md'])]
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    status = models.CharField(
        max_length=20,
        choices=RegulationStatus.choices,
        default=RegulationStatus.DRAFT
    )
    effective_date = models.DateField(default=timezone.now)
    expiration_date = models.DateField(blank=True, null=True)
    property = models.ForeignKey(
        'core.Property',  # Assuming you have a Property model in core app
        on_delete=models.CASCADE,
        related_name='regulations',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_regulations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_date', '-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['document_type']),
            models.Index(fields=['effective_date']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"

    def delete(self, *args, **kwargs):
        """Delete the document file when the regulation is deleted."""
        if self.document:
            if os.path.isfile(self.document.path):
                os.remove(self.document.path)
        super().delete(*args, **kwargs)


class RegulationRecipient(models.Model):
    """Model to track who has received which regulation."""
    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.CASCADE,
        related_name='recipients'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_regulations'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('regulation', 'user')
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.user.email} - {self.regulation.title}"
