from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'contact_type', 'created_at')
    list_filter = ('contact_type', 'created_at')
    search_fields = ('name', 'phone_number', 'email')
    ordering = ('-created_at',)
