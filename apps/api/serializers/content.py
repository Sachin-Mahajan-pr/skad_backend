from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.taxonomy.models import Category, Tag
from apps.content.models import (
    Article, NewsItem, PressRelease, CaseStudy, Report, Event,
    Page, Section, NavigationItem, FooterColumn, Announcement,
    UIString, SiteSettings, MediaAsset
)

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["type", "order", "enabled", "background", "anchor_id", "content"]

class PageSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ["slug", "title", "template", "sections", "seo_title", "seo_description", "canonical_url"]

    @extend_schema_field(SectionSerializer(many=True))
    def get_sections(self, obj):
        active_sections = obj.sections.filter(enabled=True).order_by("order")
        return SectionSerializer(active_sections, many=True).data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["slug", "name", "description"]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["slug", "name"]

class ArticleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(read_only=True, slug_field="name")
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    author_name = serializers.CharField(source="author.name", read_only=True, default=None)

    class Meta:
        model = Article
        fields = [
            "slug", "title", "category", "tags", "author_name", "hero_image", "hero_alt",
            "excerpt", "body", "reading_minutes", "publish_at", "seo_title", "seo_description"
        ]

class NewsItemSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = NewsItem
        fields = ["slug", "title", "kind", "kind_display", "body", "publish_at", "seo_title", "seo_description"]

class PressReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PressRelease
        fields = ["slug", "title", "location", "body", "media_contact_email", "downloadable_pdf", "publish_at", "seo_title", "seo_description"]

class CaseStudySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True, default=None)
    brand_name = serializers.CharField(source="brand.name", read_only=True, default=None)

    class Meta:
        model = CaseStudy
        fields = ["slug", "title", "hero_image", "summary", "challenge", "solution", "impact_results", "company_name", "brand_name", "publish_at"]

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["slug", "title", "year", "summary", "file", "is_public", "publish_at"]

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["slug", "title", "event_date", "location", "description", "external_url"]

class NavigationItemSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = NavigationItem
        fields = ["id", "label", "link", "order", "visible", "short_description", "children"]

    def get_children(self, obj):
        children = obj.children.filter(visible=True)
        return NavigationItemSerializer(children, many=True).data

class FooterColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = FooterColumn
        fields = ["title", "order", "links"]

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ["text", "link", "dismissible", "active"]

class UIStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIString
        fields = ["key", "value"]

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "group_name", "primary_headline", "operating_philosophy", "primary_email",
            "support_phone", "copyright_text", "social_links", "maintenance_mode"
        ]

class MediaAssetSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id", "title", "file_url", "folder", "alt_text", "is_decorative",
            "focal_point", "credit_licence", "width", "height", "derivatives", "created_at"
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_file_url(self, obj):
        return obj.file.url if obj.file else None
