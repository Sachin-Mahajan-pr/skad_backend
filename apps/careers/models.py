from django.db import models
from apps.core.models import Publishable
from apps.core.storage import get_private_storage
from apps.core.utils import random_resume_upload_path

class DepartmentChoices(models.TextChoices):
    TECHNOLOGY = "technology", "Technology & Engineering"
    AI = "ai", "AI & Automation"
    COMMERCE = "commerce", "Commerce & Operations"
    CREATIVE = "creative", "Brand & Creative"
    MARKETING = "marketing", "Marketing & Growth"
    FINANCE = "finance", "Finance & Corporate"
    SALES = "sales", "Sales & Partnerships"
    MANUFACTURING = "manufacturing", "Manufacturing & Supply"
    TRADE = "trade", "International Trade"
    CUSTOMER_EXP = "cx", "Customer Experience"

class Career(Publishable):
    """
    Open career roles across SKAD GROUP and ecosystem companies.
    """
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    department = models.CharField(max_length=40, choices=DepartmentChoices.choices)
    location = models.CharField(max_length=120, help_text="e.g. Surat, Mumbai, London, Remote")
    employment_type = models.CharField(
        max_length=40,
        choices=[
            ("full_time", "Full-time"),
            ("part_time", "Part-time"),
            ("contract", "Contract"),
            ("internship", "Internship"),
        ],
        default="full_time",
    )
    description = models.TextField()
    requirements = models.TextField(blank=True)
    company = models.ForeignKey(
        "entities.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="careers",
    )
    application_route = models.CharField(
        max_length=20,
        choices=[("form", "Direct Application Form"), ("external", "External Career Portal")],
        default="form",
    )
    external_apply_url = models.URLField(blank=True)
    closes_on = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Career Opening"
        verbose_name_plural = "Career Openings"
        ordering = ["-publish_at"]

    def __str__(self):
        return f"{self.title} ({self.location})"

class Application(models.Model):
    """
    Candidate job applications submitted through the careers portal.
    """
    career = models.ForeignKey(
        Career,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applications",
        help_text="Null for general profile submissions",
    )
    candidate_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=32, blank=True)
    linkedin_profile = models.URLField(blank=True)
    cv_file = models.FileField(
        upload_to=random_resume_upload_path,
        storage=get_private_storage,
        help_text="Candidate CV/resume stored in secure private bucket.",
    )
    cover_letter = models.TextField(blank=True)
    consent_recorded = models.BooleanField(
        default=False,
        help_text="Consent for processing candidate data during recruitment.",
    )
    retention_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date after which candidate data is auto-deleted per retention policy (Page 13).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ["-created_at"]

    def __str__(self):
        role = self.career.title if self.career else "General Submission"
        return f"{self.candidate_name} -> {role}"
