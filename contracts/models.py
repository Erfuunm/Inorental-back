from django.db import models
from django.conf import settings
from django.utils import timezone

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent for Signature'),
        ('signed', 'Signed'),
        ('expired', 'Expired'),
        ('declined', 'Declined'),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Contract content in HTML or plain text")
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    customer_number = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the customer")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_document = models.FileField(upload_to='signed_contracts/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.customer_name} ({self.status})"

    def is_expired(self):
        if self.expiration_date:
            return timezone.now() > self.expiration_date
        return False

    def send_for_signature(self):
        # Placeholder for sending contract for signature
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
        # TODO: Implement actual email sending logic

    def mark_as_signed(self, signed_document=None):
        self.status = 'signed'
        self.signed_at = timezone.now()
        if signed_document:
            self.signed_document = signed_document
        self.save()

class ContractReminder(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='reminders')
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True, null=True)
