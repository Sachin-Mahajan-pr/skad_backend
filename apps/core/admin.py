from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.conf import settings
from simple_history.admin import SimpleHistoryAdmin

from apps.core.models import PublishStatus
from apps.core.utils import generate_preview_token
from apps.core.permissions import user_has_role, ROLE_APPROVER
from apps.seo.models import Redirect
from apps.core.tasks import trigger_revalidation_sync, revalidate_frontend

@admin.action(description="⚡ Emergency: Revalidate All Cache Tags in Next.js")
def revalidate_all_cache(modeladmin, request, queryset=None):
    """
    Emergency admin action to revalidate all frontend cache tags.
    Per page 20 of SKAD Backend Specification:
    'provide an admin action "Revalidate all" for emergencies.'
    """
    tags = [
        "companies", "brands", "platforms", "ventures", "foundation",
        "navigation", "ecosystem", "markets", "people", "articles",
        "news", "careers", "sitemap", "theme", "ui-strings", "settings"
    ]
    try:
        revalidate_frontend.delay(tags)
        messages.success(request, f"Revalidation task enqueued for tags: {', '.join(tags[:6])}...")
    except Exception as e:
        success = trigger_revalidation_sync(tags)
        if success:
            messages.success(request, "Synchronous revalidation succeeded!")
        else:
            messages.warning(request, f"Revalidation trigger failed: {e}")

class PublishableAdmin(SimpleHistoryAdmin):
    """
    Base Admin for all Publishable models.
    Enforces governance rules:
    1. Only Approver group / Superadmin can publish or verify.
    2. Automatically assigns approved_by and approved_at when verified=True.
    3. Blocks deleting published & indexed objects unless an active redirect exists.
    4. Generates a signed, short-lived preview link for Next.js draft mode.
    5. Exposes 'Revalidate all' emergency action.
    """
    actions = [revalidate_all_cache]

    def save_model(self, request, obj, form, change):
        # 1. Enforce role permission for publishing and verifying
        is_approver = user_has_role(request.user, ROLE_APPROVER)
        if (obj.verified or obj.status == PublishStatus.PUBLISHED) and not is_approver:
            messages.error(
                request,
                "Permission Denied: Only members of the 'Approver' group can verify or publish content."
            )
            # Revert to draft/in_review if not authorized
            obj.verified = False
            if obj.status == PublishStatus.PUBLISHED:
                obj.status = PublishStatus.IN_REVIEW

        # 2. Automatically record approver metadata
        if obj.verified:
            if not obj.approved_by:
                obj.approved_by = request.user
            if not obj.approved_at:
                obj.approved_at = timezone.now()

        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        self._check_deletion_guard(obj)
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self._check_deletion_guard(obj)
        super().delete_queryset(request, queryset)

    def _check_deletion_guard(self, obj):
        """
        Admin guard per Page 8:
        'block deleting a published, indexed object unless a redirect exists.'
        """
        is_published = getattr(obj, "status", None) == PublishStatus.PUBLISHED
        is_indexed = not getattr(obj, "noindex", False)
        slug = getattr(obj, "slug", "")

        if is_published and is_indexed and slug:
            model_name = obj._meta.model_name
            prefix_map = {
                "company": "/companies/",
                "brand": "/brands/",
                "platform": "/platforms/",
                "article": "/insights/",
                "page": "/",
                "career": "/careers/",
            }
            prefix = prefix_map.get(model_name, "/")
            public_path = f"{prefix}{slug}" if prefix != "/" else f"/{slug}"

            has_redirect = Redirect.objects.filter(old_path=public_path).exists()
            if not has_redirect:
                raise ValidationError(
                    f"Governance Guard: Cannot delete published, indexed {obj._meta.verbose_name} '{public_path}' "
                    f"without an active 301 Redirect. Please create a redirect under SEO > Redirects first."
                )

    def preview_link(self, obj):
        """Next.js draft-mode preview button per Page 9."""
        if not obj or not getattr(obj, "slug", None):
            return "-"
        frontend_origin = getattr(settings, "FRONTEND_ORIGIN", "http://localhost:3000")
        model_name = obj._meta.model_name
        token = generate_preview_token(model_name, obj.slug)
        preview_url = f"{frontend_origin}/api/draft?secret={token}&slug={obj.slug}&type={model_name}"
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 4px 8px; font-weight: 600;">Draft Preview ↗</a>',
            preview_url
        )
    preview_link.short_description = "Live Draft Preview"
