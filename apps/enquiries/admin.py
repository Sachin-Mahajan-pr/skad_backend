import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import EnquiryRoute, Enquiry, Opportunity, Subscription

@admin.action(description="Export selected enquiries to CSV (Approvers only)")
def export_enquiries_csv(modeladmin, request, queryset):
    """
    Exports filtered enquiries to CSV.
    Per page 13 of SKAD Backend Specification: 'CSV export restricted to Approvers'
    """
    from apps.core.permissions import user_has_role, ROLE_APPROVER
    from django.contrib import messages
    if not user_has_role(request.user, ROLE_APPROVER):
        messages.error(request, "Permission Denied: CSV export of enquiries is restricted to members of the 'Approver' group.")
        return None

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="skad_enquiries_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "Reference", "Route", "Name", "Company", "Role", "Email",
        "Phone", "Country", "Website", "Status", "Consent Timestamp", "Created At"
    ])
    for e in queryset:
        writer.writerow([
            e.reference, e.route.label, e.name, e.company, e.role, e.email,
            e.phone, e.country, e.company_website, e.get_status_display(),
            e.consent_at.isoformat() if e.consent_at else "",
            e.created_at.isoformat()
        ])
    return response


@admin.register(EnquiryRoute)
class EnquiryRouteAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "active", "group", "to_emails")
    list_filter = ("active",)
    search_fields = ("code", "label")

from django.utils.html import format_html

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("reference", "name", "route", "company", "email", "status", "attachment_download_link", "assigned_to", "created_at")
    list_filter = ("status", "route", "country", "created_at")
    search_fields = ("reference", "name", "company", "email", "message")
    readonly_fields = ("reference", "ip_hash", "consent_at", "privacy_version", "created_at", "attachment_download_link")
    actions = [export_enquiries_csv]

    def attachment_download_link(self, obj):
        if not obj.attachment:
            return "-"
        storage = obj.attachment.storage
        if hasattr(storage, "generate_presigned_url"):
            url = storage.generate_presigned_url(obj.attachment.name, expires_in=300)
        else:
            url = obj.attachment.url
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 3px 8px; font-weight: 600; color: #D4AF37; background: #0A1F44; border-radius: 4px;">Download Attachment (Signed URL) ↗</a>',
            url
        )
    attachment_download_link.short_description = "Attachment"

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "opportunity_type", "company", "email", "attachment_download_link", "created_at")
    list_filter = ("opportunity_type", "created_at")
    search_fields = ("name", "company", "email", "summary")
    readonly_fields = ("created_at", "attachment_download_link")

    def attachment_download_link(self, obj):
        if not obj.attachment:
            return "-"
        storage = obj.attachment.storage
        if hasattr(storage, "generate_presigned_url"):
            url = storage.generate_presigned_url(obj.attachment.name, expires_in=300)
        else:
            url = obj.attachment.url
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 3px 8px; font-weight: 600; color: #D4AF37; background: #0A1F44; border-radius: 4px;">Download Attachment (Signed URL) ↗</a>',
            url
        )
    attachment_download_link.short_description = "Attachment"

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("email", "confirmed", "created_at")
    list_filter = ("confirmed", "created_at")
    search_fields = ("email",)
    readonly_fields = ("created_at",)
