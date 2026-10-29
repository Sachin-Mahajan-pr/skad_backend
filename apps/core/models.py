from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
from .validators import validate_no_banned_phrases, validate_no_placeholders
from .utils import sanitize_html

class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    IN_REVIEW = "in_review", "In review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"
    ARCHIVED = "archived", "Archived"

class PublishedQuerySet(models.QuerySet):
    def public(self):
        """Returns only verified, published content whose publish_at timestamp has passed."""
        return self.filter(
            status=PublishStatus.PUBLISHED,
            verified=True,
            publish_at__lte=timezone.now(),
        )

class PublishedManager(models.Manager.from_queryset(PublishedQuerySet)):
    pass

class Publishable(models.Model):
    """
    Abstract base for all editorial content that must pass through
    approval and verification workflows before appearing on public APIs.
    """
    status = models.CharField(
        max_length=12,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    verified = models.BooleanField(
        default=False,
        help_text="Facts checked and approved by the designated legal/entity content owner",
        db_index=True,
    )
    approved_by = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    publish_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PublishedManager()
    all_objects = models.Manager()
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        # Publishing workflow governance:
        # A record cannot be PUBLISHED unless it is verified=True
        if self.status == PublishStatus.PUBLISHED and not self.verified:
            raise ValidationError(
                {"verified": "An item cannot be published publicly without verified=True approval."}
            )

class SeoFields(models.Model):
    """
    Shared SEO & OpenGraph fields for all public indexable objects.
    """
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Optimal length 50-60 characters",
    )
    seo_description = models.CharField(
        max_length=170,
        blank=True,
        help_text="Optimal length 150-160 characters",
    )
    canonical_url = models.URLField(blank=True)
    og_image = models.ImageField(upload_to="og/", blank=True)
    noindex = models.BooleanField(
        default=False,
        help_text="Exclude this page from search engine indexes",
    )

    class Meta:
        abstract = True

class Entity(Publishable, SeoFields):
    """
    Base class for canonical corporate entities: Company, Brand, Platform, Venture, Foundation.
    """
    name = models.CharField(max_length=160, db_index=True)
    slug = models.SlugField(max_length=180, unique=True)
    summary = models.TextField(blank=True)
    body = models.TextField(blank=True, help_text="Sanitised rich text or markdown description")
    sort_order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        if self.status == PublishStatus.PUBLISHED:
            # Enforce content governance rules on public copy
            validate_no_banned_phrases(self.name)
            validate_no_banned_phrases(self.summary)
            validate_no_banned_phrases(self.body)
            validate_no_placeholders(self.summary)
            validate_no_placeholders(self.body)

    def save(self, *args, **kwargs):
        if self.body:
            self.body = sanitize_html(self.body)
        super().save(*args, **kwargs)
