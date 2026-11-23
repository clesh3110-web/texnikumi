from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'ip_address', 'details_short')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'details', 'ip_address')
    readonly_fields = ('created_at', 'user', 'action', 'ip_address', 'details')

    def details_short(self, obj):
        return obj.details[:60]
    details_short.short_description = 'Tafsilotlar'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
