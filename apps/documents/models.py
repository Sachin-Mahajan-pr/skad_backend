import hashlib
from django.db import models
from apps.core.models import Publishable
from apps.core.storage import get_private_storage
from apps.core.utils import random_document_upload_path

class DocumentType(models.TextChoices):
    GROUP_PROFILE = "group_profile", "Corporate Profile"
    PRESENTATION = "presentation", "Corporate Presentation"
    POLICY = "policy", "Corporate Policy / Code of Conduct"
    REPORT = "report", "Annual / Operations Report"
    IMPACT_REPORT = "impact_report", "Impact & Foundation Report"
    MEDIA_KIT = "media_kit", "Media Kit"
    BRAND_ASSETS = "brand_assets", "Brand Guidelines & Assets"
    GOVERNANCE = "governance", "Governance & Compliance Document"

class Document(Publishable):
    """
    Corporate governance, policy documents, and media resources.
    Per page 8: Downloads are routed through a tracked endpoint that logs the event.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    doc_type = models.CharField(max_length=30, choices=DocumentType.choices)
    visibility = models.CharField(
        max_length=12,
        choices=[("public", "Public Download"), ("on_request", "On Request"), ("internal", "Internal Only")],
        default="public",
    )
    current_version = models.ForeignKey(
        "DocumentVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        verbose_name = "Corporate Document"
        verbose_name_plural = "Corporate Documents"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.get_doc_type_display()})"

class DocumentVersion(models.Model):
    """
    Specific release version of a corporate document.
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    file = models.FileField(
        upload_to=random_document_upload_path,
        storage=get_private_storage,
        help_text="Corporate document stored in private bucket; served via signed URLs.",
    )
    version_label = models.CharField(max_length=40, help_text="e.g. 'v1.0 - October 2026'")
    issued_on = models.DateField()
    sha256 = models.CharField(max_length=64, editable=False, blank=True)
    allow_download = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Document Version"
        verbose_name_plural = "Document Versions"
        ordering = ["-issued_on"]

    def __str__(self):
        return f"{self.document.title} - {self.version_label}"

    def save(self, *args, **kwargs):
        if self.file and not self.sha256:
            try:
                hasher = hashlib.sha256()
                for chunk in self.file.chunks():
                    hasher.update(chunk)
                self.sha256 = hasher.hexdigest()
            except Exception:
                pass
        super().save(*args, **kwargs)
