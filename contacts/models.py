from django.db import models
from django.core.validators import RegexValidator

class Contact(models.Model):
    CONTACT_TYPES = [
        ('lead', 'Lead'),
        ('tenant', 'Tenant'),
        ('vendor', 'Vendor'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.contact_type})"

    class Meta:
        ordering = ['-created_at']
