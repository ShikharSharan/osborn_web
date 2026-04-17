from django.contrib import admin
from .models import Appointment, Contact

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'preferred_date', 'service', 'status', 'created_at']
    list_filter = ['status', 'service', 'preferred_date', 'created_at']
    search_fields = ['name', 'email', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('preferred_date', 'service', 'message')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'created_at')
        }),
    )
