from django.contrib import admin
from .models import Appointment, Clinic, Contact, PathologyBooking, PharmacyOrder

admin.site.site_header = "Osborn Administration"
admin.site.site_title = "Osborn Admin"
admin.site.index_title = "Osborn Healthcare Admin Portal"


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'offers_consultation',
        'offers_pharmacy',
        'offers_pathology',
        'is_active',
        'sort_order',
    ]
    list_filter = ['is_active', 'offers_consultation', 'offers_pharmacy', 'offers_pathology']
    search_fields = ['name', 'address', 'phone', 'email', 'services_offered']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']

    fieldsets = (
        ('Clinic Details', {
            'fields': ('name', 'slug', 'address', 'phone', 'email', 'operating_hours')
        }),
        ('Services', {
            'fields': ('services_offered', 'offers_consultation', 'offers_pharmacy', 'offers_pathology')
        }),
        ('Maps', {
            'fields': ('google_maps_url', 'map_embed_url')
        }),
        ('Publishing', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'clinic', 'preferred_date', 'service', 'status', 'created_at']
    list_filter = ['status', 'clinic', 'service', 'preferred_date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'clinic__name', 'clinic__address']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_select_related = ['clinic']

    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Appointment Details', {
            'fields': ('clinic', 'preferred_date', 'service', 'message')
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


@admin.register(PharmacyOrder)
class PharmacyOrderAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'delivery_mode', 'branch', 'preferred_date', 'status', 'created_at']
    list_filter = ['status', 'delivery_mode', 'branch', 'preferred_date', 'created_at']
    search_fields = ['name', 'phone', 'email', 'medicine_list', 'delivery_address', 'branch__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_select_related = ['branch']

    fieldsets = (
        ('Patient Information', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Order Details', {
            'fields': ('delivery_mode', 'branch', 'delivery_address', 'prescription_upload', 'medicine_list', 'preferred_date')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(PathologyBooking)
class PathologyBookingAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'phone', 'collection_mode', 'branch', 'preferred_date', 'status', 'created_at']
    list_filter = ['status', 'collection_mode', 'branch', 'preferred_date', 'created_at']
    search_fields = ['patient_name', 'phone', 'email', 'selected_tests', 'collection_address', 'referral_doctor', 'branch__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    list_select_related = ['branch']

    fieldsets = (
        ('Patient Information', {
            'fields': ('patient_name', 'phone', 'email')
        }),
        ('Booking Details', {
            'fields': ('selected_tests', 'collection_mode', 'branch', 'collection_address', 'preferred_date', 'referral_doctor', 'notes')
        }),
        ('Status', {
            'fields': ('status', 'created_at')
        }),
    )
