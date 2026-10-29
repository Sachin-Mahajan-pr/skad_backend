from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import (
    Article, NewsItem, PressRelease, CaseStudy, Report, Event,
    Page, Section, NavigationItem, FooterColumn, Announcement,
    UIString, SiteSettings, ThemeToken, FeatureFlag, MediaAsset
)

from apps.core.admin import PublishableAdmin

class SectionInline(admin.StackedInline):
    model = Section
    extra = 1
    fields = ("type", "order", "enabled", "background", "anchor_id", "content")

@admin.register(Page)
class PageAdmin(PublishableAdmin):
    list_display = ("title", "slug", "template", "status", "verified", "preview_link", "updated_at")
    list_filter = ("status", "verified", "template")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("preview_link", "approved_by", "approved_at")
    inlines = [SectionInline]

@admin.register(Article)
class ArticleAdmin(PublishableAdmin):
    list_display = ("title", "category", "author", "reading_minutes", "status", "verified", "preview_link", "publish_at")
    list_filter = ("status", "verified", "category", "publish_at")
    search_fields = ("title", "body", "excerpt", "sources")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_companies", "related_brands", "tags")
    readonly_fields = ("preview_link", "approved_by", "approved_at")

@admin.register(NewsItem)
class NewsItemAdmin(PublishableAdmin):
    list_display = ("title", "kind", "status", "verified", "preview_link", "publish_at")
    list_filter = ("kind", "status", "verified", "publish_at")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("preview_link", "approved_by", "approved_at")

@admin.register(PressRelease)
class PressReleaseAdmin(PublishableAdmin):
    list_display = ("title", "location", "status", "verified", "publish_at")
    list_filter = ("status", "verified", "publish_at")
    search_fields = ("title", "body", "location")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("approved_by", "approved_at")

@admin.register(CaseStudy)
class CaseStudyAdmin(PublishableAdmin):
    list_display = ("title", "company", "brand", "status", "verified", "publish_at")
    list_filter = ("status", "verified", "company", "brand")
    search_fields = ("title", "summary", "solution", "impact_results")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("approved_by", "approved_at")

@admin.register(Report)
class ReportAdmin(PublishableAdmin):
    list_display = ("title", "year", "is_public", "status", "verified")
    list_filter = ("year", "is_public", "status", "verified")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("approved_by", "approved_at")

@admin.register(Event)
class EventAdmin(PublishableAdmin):
    list_display = ("title", "event_date", "location", "status", "verified")
    list_filter = ("status", "verified", "event_date")
    search_fields = ("title", "location", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("approved_by", "approved_at")


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "link", "parent", "order", "visible")
    list_filter = ("visible",)
    search_fields = ("label", "link")

@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    search_fields = ("title",)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("text", "link", "active", "dismissible", "start_date", "end_date")
    list_filter = ("active", "dismissible")

@admin.register(UIString)
class UIStringAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description")
    search_fields = ("key", "value", "description")

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("group_name", "primary_headline", "primary_email", "maintenance_mode")

@admin.register(ThemeToken)
class ThemeTokenAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "group", "description")
    list_filter = ("group",)
    search_fields = ("key", "value", "description")

@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ("label", "key", "enabled")
    list_filter = ("enabled",)
    search_fields = ("label", "key", "description")


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "folder", "is_decorative", "alt_text", "created_at")
    list_filter = ("folder", "is_decorative", "created_at")
    search_fields = ("title", "alt_text", "credit_licence")
