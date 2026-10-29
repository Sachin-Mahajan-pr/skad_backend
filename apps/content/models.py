from django.db import models
from django.contrib.contenttypes.models import ContentType
from apps.core.models import Publishable, SeoFields

class Article(Publishable, SeoFields):
    """
    Thought leadership and editorial insights.
    Per page 7: Author, date, reading time, hero image with alt text, internal sources note.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(
        "taxonomy.Category",
        on_delete=models.PROTECT,
        related_name="articles",
    )
    tags = models.ManyToManyField(
        "taxonomy.Tag",
        blank=True,
        related_name="articles",
    )
    author = models.ForeignKey(
        "people.Person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    hero_image = models.ImageField(upload_to="articles/", blank=True)
    hero_alt = models.CharField(max_length=200, blank=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    reading_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    related_companies = models.ManyToManyField("entities.Company", blank=True, related_name="articles")
    related_brands = models.ManyToManyField("entities.Brand", blank=True, related_name="articles")
    sources = models.TextField(blank=True, help_text="Internal factual basis / references. Never exposed on API.")

    class Meta:
        verbose_name = "Insight Article"
        verbose_name_plural = "Insight Articles"
        ordering = ["-publish_at"]

    def __str__(self):
        return self.title

class NewsKind(models.TextChoices):
    ANNOUNCEMENT = "announcement", "Announcement"
    LAUNCH = "launch", "Launch"
    PARTNERSHIP = "partnership", "Partnership"
    LEADERSHIP = "leadership", "Leadership"
    FOUNDATION = "foundation", "Foundation"
    MEDIA_COVERAGE = "media_coverage", "Media Coverage"
    PRESS_RELEASE = "press_release", "Press Release"

class NewsItem(Publishable, SeoFields):
    """
    Newsroom releases, corporate announcements, and media kit assets.
    """
    kind = models.CharField(max_length=20, choices=NewsKind.choices, default=NewsKind.ANNOUNCEMENT)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    body = models.TextField()
    related_entity = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "News Item"
        verbose_name_plural = "News Items"
        ordering = ["-publish_at"]

    def __str__(self):
        return f"[{self.get_kind_display()}] {self.title}"

class PressRelease(Publishable, SeoFields):
    """
    Official corporate press releases with release date, location, and embargo support.
    Per page 4 & 8.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    location = models.CharField(max_length=80, default="Surat, India")
    body = models.TextField()
    media_contact_email = models.EmailField(default="press@skadgroup.com")
    downloadable_pdf = models.FileField(upload_to="press_releases/", blank=True)

    class Meta:
        verbose_name = "Press Release"
        verbose_name_plural = "Press Releases"
        ordering = ["-publish_at"]

    def __str__(self):
        return self.title

class CaseStudy(Publishable, SeoFields):
    """
    Ecosystem case studies demonstrating BUILD • CONNECT • SCALE in action.
    Per page 4 & 8.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    hero_image = models.ImageField(upload_to="case_studies/", blank=True)
    summary = models.TextField()
    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    impact_results = models.TextField(help_text="Verified factual results only; no invented metrics.")
    company = models.ForeignKey("entities.Company", null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey("entities.Brand", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Case Study"
        verbose_name_plural = "Case Studies"
        ordering = ["-publish_at"]

    def __str__(self):
        return self.title

class Report(Publishable, SeoFields):
    """
    Corporate, annual, ESG, and governance reports.
    Per page 4 & 8.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    year = models.PositiveSmallIntegerField(default=2026)
    summary = models.TextField()
    file = models.FileField(upload_to="reports/")
    is_public = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-year", "title"]

    def __str__(self):
        return f"{self.title} ({self.year})"

class Event(Publishable, SeoFields):
    """
    Corporate presence, trade shows, summits, and conferences.
    Per page 4 & 8.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    event_date = models.DateTimeField()
    location = models.CharField(max_length=160)
    description = models.TextField()
    external_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.title} - {self.location}"

class Page(Publishable, SeoFields):
    """
    Managed website pages (e.g. 'home', 'about', 'strategy', 'governance').
    """
    slug = models.SlugField(max_length=120, unique=True)
    title = models.CharField(max_length=160)
    template = models.CharField(max_length=40, default="standard")

    class Meta:
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return f"{self.title} (/{self.slug})"

class Section(models.Model):
    """
    Ordered, typed content blocks that compose pages.
    Per page 14: Editors can add, remove, reorder, or schedule any section without touching code.
    """
    page = models.ForeignKey(Page, related_name="sections", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=40,
        help_text="e.g. hero, group_intro, at_a_glance, companies, brands, platforms, value_pillars, ecosystem, contact",
    )
    order = models.PositiveIntegerField(default=0)
    enabled = models.BooleanField(default=True)
    show_from = models.DateTimeField(null=True, blank=True)
    show_until = models.DateTimeField(null=True, blank=True)
    background = models.CharField(
        max_length=20,
        choices=[("white", "White"), ("offwhite", "Warm Off-White"), ("navy", "Deep Navy")],
        default="white",
    )
    anchor_id = models.SlugField(blank=True)
    content = models.JSONField(default=dict, blank=True, help_text="Validated section JSON payload")

    class Meta:
        verbose_name = "Page Section"
        verbose_name_plural = "Page Sections"
        ordering = ["order"]

    def __str__(self):
        return f"{self.page.slug} -> Section: {self.type} (order: {self.order})"

    def clean(self):
        super().clean()
        if self.content and isinstance(self.content, dict):
            from apps.content.schemas import validate_section_content
            from django.core.exceptions import ValidationError
            try:
                validate_section_content(self.type, self.content)
            except Exception as e:
                raise ValidationError({"content": f"Invalid {self.type} section content: {e}"})

class NavigationItem(models.Model):
    """
    Hierarchical navigation items for header, mega-menus, and mobile navigation.
    Per page 4 & 16.
    """
    label = models.CharField(max_length=60)
    link = models.CharField(max_length=200, help_text="Internal path e.g. /companies/skad-jewels or external URL")
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    order = models.PositiveIntegerField(default=0)
    visible = models.BooleanField(default=True)
    featured_entity = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    short_description = models.CharField(max_length=160, blank=True)

    class Meta:
        verbose_name = "Navigation Item"
        verbose_name_plural = "Navigation Items"
        ordering = ["order", "label"]

    def __str__(self):
        prefix = f"{self.parent.label} > " if self.parent else ""
        return f"{prefix}{self.label} ({self.link})"

class FooterColumn(models.Model):
    """
    Configurable footer columns with ordered links.
    Per page 4 & 16.
    """
    title = models.CharField(max_length=60)
    order = models.PositiveIntegerField(default=0)
    links = models.JSONField(default=list, help_text='List of {"label": "...", "href": "..."} items')

    class Meta:
        verbose_name = "Footer Column"
        verbose_name_plural = "Footer Columns"
        ordering = ["order"]

    def __str__(self):
        return self.title

class Announcement(models.Model):
    """
    Optional top announcement banner on the corporate site.
    Per page 16.
    """
    text = models.CharField(max_length=200)
    link = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    dismissible = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Site Announcement"
        verbose_name_plural = "Site Announcements"

    def __str__(self):
        return self.text

class UIString(models.Model):
    """
    Microcopy and button labels editable from Django Admin.
    Per page 15: Seed UIString with every label used by the frontend so buttons and text are editable.
    """
    key = models.CharField(max_length=120, unique=True, db_index=True)
    value = models.TextField()
    description = models.CharField(max_length=200, blank=True, help_text="Context of where this string appears")

    class Meta:
        verbose_name = "UI String (Microcopy)"
        verbose_name_plural = "UI Strings (Microcopy)"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.value[:40]}"

class SiteSettings(models.Model):
    """
    Global site configuration, contact paths, social profiles, and group statements.
    """
    group_name = models.CharField(max_length=120, default="SKAD GROUP")
    primary_headline = models.CharField(max_length=200, default="BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.")
    operating_philosophy = models.CharField(max_length=120, default="BUILD • CONNECT • SCALE")
    primary_email = models.EmailField(default="contact@skadgroup.com")
    support_phone = models.CharField(max_length=40, blank=True)
    copyright_text = models.CharField(max_length=120, default="© 2026 SKAD GROUP. All rights reserved.")
    social_links = models.JSONField(default=dict, blank=True)
    maintenance_mode = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.group_name

class ThemeToken(models.Model):
    """
    Design tokens and brand themes editable from Django Admin.
    Per page 14 & 16: Stores approved values for palette, typography, and brand styling.
    """
    key = models.CharField(max_length=80, unique=True, db_index=True, help_text="e.g. palette.primary_navy, typography.headline_font")
    value = models.CharField(max_length=160, help_text="HEX code, font family, or CSS value")
    group = models.CharField(max_length=40, default="palette", help_text="palette, typography, brand")
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Theme Token"
        verbose_name_plural = "Theme Tokens"
        ordering = ["group", "key"]

    def __str__(self):
        return f"{self.key}: {self.value}"

class FeatureFlag(models.Model):
    """
    Modular feature switches per page 14 of the specification.
    Allows enabling/disabling modules: markets_map, people, newsroom, careers, search, newsletter, investment_route, ask_skad.
    """
    key = models.CharField(max_length=60, unique=True, db_index=True)
    label = models.CharField(max_length=120)
    enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"
        ordering = ["key"]

    def __str__(self):
        status = "Enabled" if self.enabled else "Disabled"
        return f"{self.label} ({self.key}) - {status}"


class MediaFolder(models.TextChoices):
    COMPANY = "company", "Company"
    BRAND = "brand", "Brand"
    PEOPLE = "people", "People"
    FOUNDATION = "foundation", "Foundation"
    PLATFORM = "platform", "Platform"
    GENERAL = "general", "General"

class MediaAsset(models.Model):
    """
    Central media library asset with folders, usage tracking, focal points,
    and metadata per Page 14, 16, & 18 of the specification.
    """
    title = models.CharField(max_length=160)
    file = models.FileField(upload_to="library/%Y/%m/")
    folder = models.CharField(max_length=24, choices=MediaFolder.choices, default=MediaFolder.GENERAL)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Required on upload unless marked decorative.")
    is_decorative = models.BooleanField(default=False, help_text="Mark true for decorative graphics without informational content.")
    focal_point = models.CharField(max_length=40, default="center", help_text="e.g. 'center', '50% 50%', 'top'")
    credit_licence = models.CharField(max_length=200, blank=True, help_text="Licence and credit notes")
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    derivatives = models.JSONField(default=dict, blank=True, help_text="Automatic WebP/AVIF and placeholder derivative URLs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Library"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_folder_display()})"

    def clean(self):
        super().clean()
        if not self.is_decorative and not (self.alt_text and self.alt_text.strip()):
            from django.core.exceptions import ValidationError
            raise ValidationError({"alt_text": "Alt text is required for informational images unless marked as decorative (Page 16)."})

