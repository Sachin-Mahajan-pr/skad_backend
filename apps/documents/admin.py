from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Document, DocumentVersion

from django.utils.html import format_html

class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 1
    readonly_fields = ("sha256", "download_count", "signed_download_link")

    def signed_download_link(self, obj):
        if not obj or not obj.file:
            return "-"
        storage = obj.file.storage
        if hasattr(storage, "generate_presigned_url"):
            url = storage.generate_presigned_url(obj.file.name, expires_in=300)
        else:
            url = obj.file.url
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 2px 6px; font-weight: 600; color: #D4AF37; background: #0A1F44; border-radius: 4px;">Signed URL ↗</a>',
            url
        )
    signed_download_link.short_description = "Download (Signed URL)"

@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    list_display = ("title", "doc_type", "visibility", "status", "verified", "current_version")
    list_filter = ("doc_type", "visibility", "status", "verified")
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [DocumentVersionInline]
