from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import Publishable, SeoFields, PublishStatus

class Category(models.Model):
    """
    Topic taxonomy for Insights, News, and Content (e.g. Technology, AI, Commerce, Trade, Jewellery, Leadership).
    Per page 4: Located in taxonomy app.
    """
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    General taxonomy tag for cross-entity metadata.
    """
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Industry(Publishable, SeoFields):
    """
    Industries in which the SKAD ecosystem operates.
    e.g. Jewellery & Diamonds, Manufacturing, International Trade, Beauty & Personal Care,
    Fashion & Lifestyle, Legal Technology, Commerce Technology, AI & Automation, Social Impact.
    """
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Industry"
        verbose_name_plural = "Industries"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

class Capability(Publishable, SeoFields):
    """
    Core SKAD Capabilities grouped by domain:
    Product, Brand, Technology, Commerce, Manufacturing, Trade, AI, Growth.
    """
    group = models.CharField(
        max_length=40,
        help_text="Domain group: Product, Brand, Technology, Commerce, Manufacturing, Trade, AI, Growth",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(
        help_text="Concise explanation of the capability. Required to publish.",
    )
    proof_notes = models.TextField(
        blank=True,
        help_text="Internal evidence or case study references. Never exposed publicly.",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Capability"
        verbose_name_plural = "Capabilities"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.group})"

    def clean(self):
        super().clean()
        if self.status == PublishStatus.PUBLISHED and not self.description.strip():
            raise ValidationError(
                {"description": "A published capability must have a non-empty description."}
            )

class MarketStatus(models.TextChoices):
    ACTIVE = "active", "Active market"
    SERVED = "served", "Served market"
    TARGET = "target", "Target market"
    FUTURE = "future", "Future market"

class Market(Publishable):
    """
    Geographical market footprint.
    Per page 7: The four statuses are kept separate so the interactive map never
    implies current operations where none exist.
    """
    region = models.CharField(max_length=80)
    country = models.CharField(
        max_length=2,
        blank=True,
        help_text="ISO 3166-1 alpha-2 code (e.g. IN, GB, US)",
    )
    status = models.CharField(max_length=8, choices=MarketStatus.choices)
    description = models.TextField(blank=True)
    companies = models.ManyToManyField("entities.Company", blank=True, related_name="markets")
    brands = models.ManyToManyField("entities.Brand", blank=True, related_name="markets")
    capabilities = models.ManyToManyField("taxonomy.Capability", blank=True, related_name="markets")
    evidence_note = models.TextField(
        help_text="REQUIRED internal verification note explaining why this market is claimed. Never exposed on API.",
    )
    show_cta = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Markets"
        ordering = ["region", "country"]

    def __str__(self):
        return f"{self.region} ({self.country}) - {self.get_status_display()}"

    def clean(self):
        super().clean()
        if self.status == MarketStatus.ACTIVE or self.verified:
            if not self.evidence_note or not self.evidence_note.strip():
                raise ValidationError(
                    {"evidence_note": "A market cannot be marked verified/active without internal evidence documentation."}
                )
