from django.contrib import admin
from .models import Visitor, Visit

class VisitInline(admin.TabularInline):
    """Inline editing for visits in the Visitor admin."""
    model = Visit
    extra = 1
    fields = ('visit_date', 'purpose', 'property', 'follow_up_required', 'follow_up_date')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    """Admin interface for the Visitor model."""
    list_display = ('first_name', 'last_name', 'email', 'phone', 'status', 'last_visit_date')
    list_filter = ('status', 'created_at', 'last_visit_date')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'last_visit_date')
    inlines = [VisitInline]
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        ('Status & Metadata', {
            'fields': ('status', 'notes', 'created_by', 'last_visit_date', 'created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set the created_by field to the current user if this is a new record."""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    """Admin interface for the Visit model."""
    list_display = ('visitor', 'visit_date', 'purpose', 'property', 'follow_up_required', 'follow_up_date')
    list_filter = ('purpose', 'follow_up_required', 'visit_date')
    search_fields = ('visitor__first_name', 'visitor__last_name', 'visitor__email', 'property__title')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Visit Details', {
            'fields': ('visitor', 'visit_date', 'purpose', 'property')
        }),
        ('Follow-up Information', {
            'fields': ('follow_up_required', 'follow_up_date', 'follow_up_notes', 'assigned_to')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set the assigned_to field to the current user if not provided."""
        if not obj.assigned_to:
            obj.assigned_to = request.user
        super().save_model(request, obj, form, change)
