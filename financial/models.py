from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentMethod(models.Model):
    """
    Model to store payment methods.
    This will be used for future Stripe integration.
    """
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requires_processing = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['name']

    def __str__(self):
        return self.name


class PaymentCategory(models.Model):
    """
    Model to store payment categories.
    This will be used for future Stripe integration.
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Category'
        verbose_name_plural = 'Payment Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        PENDING = 'pending', 'Pending'
    
    transaction_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    payer_id = models.CharField(max_length=100)
    property_id = models.CharField(max_length=100, null=True, blank=True)
    payment_category = models.ForeignKey(
        PaymentCategory,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    notes = models.TextField(blank=True, null=True)
    synced_to_quickbooks = models.BooleanField(default=False)
    quickbooks_ref = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_created'
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} {self.currency}"


def payment_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to append payment to Excel file after save
    """
    if created:  # Only append when a new payment is created
        from .utils import append_payment_to_excel
        append_payment_to_excel(instance)


class RentRequest(models.Model):
    """
    Model to track rent payment requests.
    """
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rent_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Rent amount requested'
    )
    property = models.ForeignKey(
        'core.Property',
        on_delete=models.CASCADE,
        related_name='rent_requests',
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rent Request'
        verbose_name_plural = 'Rent Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Rent Request #{self.id} - {self.user.email} - {self.status}"


# Connect the signal
post_save.connect(payment_post_save, sender=Payment)
