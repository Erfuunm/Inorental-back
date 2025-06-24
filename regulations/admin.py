from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Regulation, RegulationRecipient, DocumentType, RegulationStatus


class RegulationRecipientInline(admin.TabularInline):
    model = RegulationRecipient
    extra = 0
    readonly_fields = ('user', 'sent_at', 'viewed_at', 'acknowledged', 'acknowledged_at')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type_display', 'status_display', 'effective_date', 'created_by_email')
    list_filter = ('document_type', 'status', 'effective_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'created_by_email')
    filter_horizontal = ()
    inlines = [RegulationRecipientInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'document', 'document_type', 'status')
        }),
        ('Dates', {
            'fields': ('effective_date', 'expiration_date')
        }),
        ('Metadata', {
            'fields': ('property', 'created_by_email', 'created_at', 'updated_at')
        }),
    )

    def document_type_display(self, obj):
        return obj.get_document_type_display()
    document_type_display.short_description = 'Type'

    def status_display(self, obj):
        return obj.get_status_display()
    status_display.short_description = 'Status'

    def created_by_email(self, obj):
        if obj.created_by:
            return obj.created_by.email
        return None
    created_by_email.short_description = 'Created By'

    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on first save
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(RegulationRecipient)
class RegulationRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'regulation_title', 'sent_at', 'viewed', 'acknowledged')
    list_filter = ('acknowledged', 'sent_at', 'viewed_at')
    search_fields = ('user__email', 'regulation__title')
    readonly_fields = ('sent_at', 'viewed_at', 'acknowledged_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def regulation_title(self, obj):
        return obj.regulation.title
    regulation_title.short_description = 'Regulation'
    regulation_title.admin_order_field = 'regulation__title'
    
    def viewed(self, obj):
        return obj.viewed_at is not None
    viewed.boolean = True
    viewed.short_description = 'Viewed'
    
    def has_add_permission(self, request):
        return False
