from django.db import models
from django.utils import timezone
from apps.core.utils import generate_enquiry_reference, random_enquiry_upload_path, random_opportunity_upload_path
from apps.core.storage import get_private_storage

class EnquiryRoute(models.Model):
    """
    Departmental routing channels for incoming corporate communications.
    """
    code = models.CharField(max_length=30, unique=True)
    label = models.CharField(max_length=80)
    to_emails = models.JSONField(default=list, help_text="List of internal email recipients")
    cc_emails = models.JSONField(default=list, blank=True)
    group = models.ForeignKey(
        "auth.Group",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Designated user group responsible for handling this route",
    )
    crm_webhook_url = models.URLField(blank=True, help_text="Optional CRM webhook endpoint")
    active = models.BooleanField(
        default=True,
        help_text="Enable or disable this route (e.g. Investment inactive until legally established)",
    )

    class Meta:
        verbose_name = "Enquiry Route"
        verbose_name_plural = "Enquiry Routes"
        ordering = ["code"]

    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"{self.label} ({self.code}) - {status}"

class EnquiryStatus(models.TextChoices):
    NEW = "new", "New"
    ASSIGNED = "assigned", "Assigned"
    IN_PROGRESS = "in_progress", "In progress"
    CLOSED = "closed", "Closed"
    SPAM = "spam", "Spam"

class Enquiry(models.Model):
    """
    Partner With SKAD and general corporate contact submissions.
    """
    reference = models.CharField(max_length=16, unique=True, editable=False, db_index=True)
    route = models.ForeignKey(EnquiryRoute, on_delete=models.PROTECT, related_name="enquiries")
    name = models.CharField(max_length=120)
    company = models.CharField(max_length=160, blank=True)
    role = models.CharField(max_length=120, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    country = models.CharField(max_length=2, help_text="ISO 3166-1 alpha-2 country code")
    company_website = models.URLField(blank=True)
    message = models.TextField()
    attachment = models.FileField(
        upload_to=random_enquiry_upload_path,
        storage=get_private_storage,
        blank=True,
        help_text="Enquiry attachment stored in private bucket per Page 13 & 19.",
    )
    consent_at = models.DateTimeField(default=timezone.now)
    privacy_version = models.CharField(max_length=20)
    status = models.CharField(max_length=16, choices=EnquiryStatus.choices, default=EnquiryStatus.NEW)
    assigned_to = models.ForeignKey(
        "auth.User",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_enquiries",
    )
    ip_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 hashed IP for rate limiting/audit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Enquiry"
        verbose_name_plural = "Enquiries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.reference}] {self.name} ({self.route.label})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = generate_enquiry_reference()
        super().save(*args, **kwargs)

class Opportunity(models.Model):
    """
    Strategic business venture or founder opportunity submission.
    """
    OPPORTUNITY_TYPES = [
        ("founder_proposal", "Founder Proposal"),
        ("strategic_partnership", "Strategic Partnership"),
        ("supplier_manufacturer", "Supplier / Manufacturer Opportunity"),
        ("technology_collaboration", "Technology Collaboration"),
        ("market_opportunity", "Market Opportunity"),
        ("brand_collaboration", "Brand Collaboration"),
        ("investment_related", "Investment-Related Enquiry"),
    ]
    opportunity_type = models.CharField(max_length=40, choices=OPPORTUNITY_TYPES)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=160, blank=True)
    company_website = models.URLField(blank=True)
    summary = models.TextField()
    attachment = models.FileField(
        upload_to=random_opportunity_upload_path,
        storage=get_private_storage,
        blank=True,
        help_text="Opportunity attachment stored in private bucket.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Business Opportunity"
        verbose_name_plural = "Business Opportunities"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_opportunity_type_display()} - {self.name}"

class Subscription(models.Model):
    """
    Newsletter double opt-in subscription.
    """
    email = models.EmailField(unique=True)
    confirmed = models.BooleanField(default=False)
    opt_in_token = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"

    def __str__(self):
        return self.email
