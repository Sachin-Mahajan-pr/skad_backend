from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Career, Application

@admin.register(Career)
class CareerAdmin(SimpleHistoryAdmin):
    list_display = ("title", "department", "location", "employment_type", "status", "verified", "closes_on")
    list_filter = ("department", "employment_type", "status", "verified")
    search_fields = ("title", "description", "requirements")
    prepopulated_fields = {"slug": ("title",)}

from django.utils.html import format_html
from apps.core.permissions import user_has_role, ROLE_HR, ROLE_SUPERADMIN

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate_name", "career", "email", "phone", "consent_recorded", "cv_download_link", "retention_date", "created_at")
    list_filter = ("created_at", "consent_recorded")
    search_fields = ("candidate_name", "email", "cover_letter")
    readonly_fields = ("created_at", "cv_download_link")

    def cv_download_link(self, obj):
        if not obj.cv_file:
            return "-"
        storage = obj.cv_file.storage
        if hasattr(storage, "generate_presigned_url"):
            url = storage.generate_presigned_url(obj.cv_file.name, expires_in=300)
        else:
            url = obj.cv_file.url
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 3px 8px; font-weight: 600; color: #D4AF37; background: #0A1F44; border-radius: 4px;">Download CV (Signed URL) ↗</a>',
            url
        )
    cv_download_link.short_description = "CV / Resume"

    def has_module_permission(self, request):
        return request.user.is_superuser or user_has_role(request.user, ROLE_HR) or user_has_role(request.user, ROLE_SUPERADMIN)

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or user_has_role(request.user, ROLE_HR) or user_has_role(request.user, ROLE_SUPERADMIN)
