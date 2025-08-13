from django.contrib import admin
from .models import UserAuditLog

@admin.register(UserAuditLog)
class UserAuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "affected_user", "performed_by", "timestamp")
    list_filter = ("action", "timestamp", "performed_by")
    search_fields = ("affected_user__username", "performed_by__username")
    readonly_fields = ("action", "affected_user", "performed_by", "details_snapshot", "timestamp")

    fieldsets = (
        ("Audit Info", {
            "fields": ("action", "affected_user", "performed_by", "timestamp")
        }),
        ("Details Snapshot", {
            "fields": ("details_snapshot",),
        }),
    )

    def has_add_permission(self, request):
        # Audit logs are created by signals, so no manual adding
        return False

    def has_change_permission(self, request, obj=None):
        # Prevent manual edits
        return False
