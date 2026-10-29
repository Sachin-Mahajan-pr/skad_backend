from django.db import models
from apps.core.models import Publishable

class FoundationInitiative(Publishable):
    """
    Kalla Rudra Foundation charitable programs and social impact initiatives.
    Per page 8: Kept clearly separated from commercial brands.
    Do not publish donation totals or statistics unless verified and approved.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    focus_area = models.CharField(
        max_length=120,
        help_text="e.g. Healthcare, Rural Education, Women Empowerment, Sustainability",
    )
    status_label = models.CharField(max_length=60, default="Active Initiative")
    date = models.DateField(null=True, blank=True)
    verified_impact_details = models.TextField(
        help_text="Verified outcomes and program notes. No unsupported metrics.",
    )
    media = models.ImageField(upload_to="foundation/", blank=True)

    class Meta:
        verbose_name = "Foundation Initiative"
        verbose_name_plural = "Foundation Initiatives"
        ordering = ["-date", "title"]

    def __str__(self):
        return f"{self.title} ({self.focus_area})"
