from django.contrib import admin
from .models import Payment, PaymentCategory, PaymentMethod


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'requires_processing', 'created_at')
    list_filter = ('is_active', 'requires_processing', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_id',
        'amount',
        'currency',
        'status',
        'payment_method',
        'payment_category',
        'payer_id',
        'created_at',
        'synced_to_quickbooks'
    )
    list_filter = (
        'status',
        'payment_method',
        'payment_category',
        'synced_to_quickbooks',
        'created_at',
    )
    search_fields = (
        'transaction_id',
        'payer_id',
        'property_id',
        'quickbooks_ref',
        'notes'
    )
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'transaction_id',
                'amount',
                'currency',
                'status',
                'payment_method',
                'payment_category',
            )
        }),
        ('Related Information', {
            'fields': (
                'payer_id',
                'property_id',
                'notes',
            )
        }),
        ('QuickBooks Integration', {
            'fields': (
                'synced_to_quickbooks',
                'quickbooks_ref',
            ),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only set created_by during the first save
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
