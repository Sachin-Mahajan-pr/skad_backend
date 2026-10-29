from django.contrib import admin, messages
from django.utils import timezone
from apps.core.admin import PublishableAdmin
from apps.core.permissions import user_has_role, ROLE_APPROVER
from apps.people.models import PersonRole
from .models import (
    Group, Company, Brand, Platform, Venture, Foundation,
    Relationship, RelationshipType
)

@admin.action(description="Mark selected items as Verified & Approved (Approver only)")
def mark_verified_and_approved(modeladmin, request, queryset):
    if not user_has_role(request.user, ROLE_APPROVER):
        messages.error(request, "Permission Denied: Only members of the 'Approver' group can verify content.")
        return
    queryset.update(
        verified=True,
        approved_by=request.user,
        approved_at=timezone.now(),
    )
    messages.success(request, f"Successfully verified {queryset.count()} item(s).")

class PersonRoleInline(admin.TabularInline):
    """Inline leadership editing for companies per Doc 1 Page 9."""
    model = PersonRole
    extra = 1
    fields = ("person", "role_title", "is_primary", "start_date")

@admin.register(Group)
class GroupAdmin(PublishableAdmin):
    list_display = ("name", "primary_line", "operating_philosophy", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified")
    search_fields = ("name", "primary_line", "summary")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

@admin.register(Company)
class CompanyAdmin(PublishableAdmin):
    list_display = ("name", "legal_name", "company_type", "city", "country", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified", "country", "sector")
    search_fields = ("name", "legal_name", "company_type", "sector")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("capabilities", "industries")
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    inlines = [PersonRoleInline]
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

@admin.register(Brand)
class BrandAdmin(PublishableAdmin):
    list_display = ("name", "category", "market_scope", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified", "market_scope", "category")
    search_fields = ("name", "tagline", "category", "positioning")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("capabilities", "industries")
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

@admin.register(Platform)
class PlatformAdmin(PublishableAdmin):
    list_display = ("name", "tagline", "status_label", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified")
    search_fields = ("name", "purpose", "tagline")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("capabilities", "industries")
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

    def status_label(self, obj):
        return obj.status
    status_label.short_description = "Initiative Status"

@admin.register(Venture)
class VentureAdmin(PublishableAdmin):
    list_display = ("name", "venture_type", "stage_label", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified", "venture_type")
    search_fields = ("name", "venture_type", "summary")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

@admin.register(Foundation)
class FoundationAdmin(PublishableAdmin):
    list_display = ("name", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified")
    search_fields = ("name", "mission", "summary")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("industries",)
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

@admin.register(Relationship)
class RelationshipAdmin(PublishableAdmin):
    list_display = ("__str__", "relationship", "verified", "updated_at")
    list_filter = ("relationship", "verified")
    search_fields = ("note",)
    actions = PublishableAdmin.actions + [mark_verified_and_approved]

    def save_model(self, request, obj, form, change):
        """
        Soft warning in admin per Doc 1 Page 9:
        'Soft warnings in admin when an ownership-type relationship is saved but not verified.'
        """
        if obj.relationship in (RelationshipType.OPERATES, RelationshipType.OWNS_BRAND) and not obj.verified:
            messages.warning(
                request,
                f"Governance Warning: The relationship '{obj.get_relationship_display()}' was saved as unverified. "
                "Per ecosystem policy, ownership and operational links will NOT be exposed on public APIs "
                "until reviewed and marked verified=True by an authorized Approver."
            )
        super().save_model(request, obj, form, change)
