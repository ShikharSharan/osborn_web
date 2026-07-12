from django.contrib import admin
from .models import (
    Appointment,
    Clinic,
    Contact,
    PathologyBooking,
    PharmacyOrder,
    SaathiChatLog,
    SaathiSettings,
    SiteErrorLog,
)

admin.site.site_header = "Osborn Administration"
admin.site.site_title = "Osborn Admin"
admin.site.index_title = "Osborn Healthcare Admin Portal"


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'alternate_phone',
        'offers_consultation',
        'offers_pharmacy',
        'offers_pathology',
        'is_active',
        'sort_order',
    ]
    list_filter = ['is_active', 'offers_consultation', 'offers_pharmacy', 'offers_pathology']
    search_fields = ['name', 'address', 'phone', 'alternate_phone', 'email', 'services_offered']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']

    fieldsets = (
        ('Clinic Details', {
            'fields': ('name', 'slug', 'address', 'phone', 'alternate_phone', 'email', 'operating_hours')
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


@admin.register(SaathiSettings)
class SaathiSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'ai_enabled', 'updated_at']
    readonly_fields = ['updated_at']

    fieldsets = (
        ('AI Control', {
            'fields': ('name', 'ai_enabled')
        }),
        ('Fallback Response', {
            'fields': ('fallback_reply',)
        }),
        ('System', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(SaathiChatLog)
class SaathiChatLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'source', 'ai_model', 'error_preview', 'message_preview', 'reply_preview', 'ip_address']
    list_filter = ['source', 'ai_model', 'created_at']
    search_fields = ['message', 'reply', 'error_detail', 'ip_address']
    readonly_fields = ['message', 'reply', 'source', 'ai_model', 'error_detail', 'ip_address', 'created_at']
    ordering = ['-created_at']
    actions = ['clear_selected_logs', 'clear_all_logs']

    def has_add_permission(self, request):
        return False

    @admin.action(description="Clear selected Saathi logs")
    def clear_selected_logs(self, request, queryset):
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Cleared {deleted_count} Saathi chat log(s).")

    @admin.action(description="Clear all Saathi logs")
    def clear_all_logs(self, request, queryset):
        deleted_count = SaathiChatLog.objects.count()
        SaathiChatLog.objects.all().delete()
        self.message_user(request, f"Cleared all Saathi chat logs ({deleted_count}).")

    def message_preview(self, obj):
        return obj.message[:80]

    def reply_preview(self, obj):
        return obj.reply[:80]

    def error_preview(self, obj):
        return obj.error_detail[:80]


@admin.register(SiteErrorLog)
class SiteErrorLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'status_code', 'exception_type', 'path', 'method', 'is_resolved', 'user_label', 'ip_address']
    list_filter = ['status_code', 'exception_type', 'is_resolved', 'created_at']
    search_fields = ['path', 'message', 'traceback', 'user_label', 'ip_address']
    readonly_fields = [
        'path',
        'method',
        'status_code',
        'exception_type',
        'message',
        'traceback',
        'user_label',
        'ip_address',
        'user_agent',
        'created_at',
    ]
    ordering = ['-created_at']
    actions = ['mark_resolved', 'mark_unresolved', 'clear_selected_error_logs', 'clear_all_error_logs']

    fieldsets = (
        ('Error', {
            'fields': ('exception_type', 'message', 'status_code', 'is_resolved')
        }),
        ('Request', {
            'fields': ('path', 'method', 'user_label', 'ip_address', 'user_agent', 'created_at')
        }),
        ('Traceback', {
            'fields': ('traceback',)
        }),
    )

    def has_add_permission(self, request):
        return False

    @admin.action(description="Mark selected errors resolved")
    def mark_resolved(self, request, queryset):
        updated_count = queryset.update(is_resolved=True)
        self.message_user(request, f"Marked {updated_count} error log(s) resolved.")

    @admin.action(description="Mark selected errors unresolved")
    def mark_unresolved(self, request, queryset):
        updated_count = queryset.update(is_resolved=False)
        self.message_user(request, f"Marked {updated_count} error log(s) unresolved.")

    @admin.action(description="Clear selected error logs")
    def clear_selected_error_logs(self, request, queryset):
        deleted_count = queryset.count()
        queryset.delete()
        self.message_user(request, f"Cleared {deleted_count} error log(s).")

    @admin.action(description="Clear all error logs")
    def clear_all_error_logs(self, request, queryset):
        deleted_count = SiteErrorLog.objects.count()
        SiteErrorLog.objects.all().delete()
        self.message_user(request, f"Cleared all error logs ({deleted_count}).")
