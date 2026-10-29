from django.db import models

class Redirect(models.Model):
    """
    URL redirects for maintaining canonical paths and SEO equity.
    Per page 8: When a published object's slug changes, auto-create a Redirect from the old path.
    """
    old_path = models.CharField(max_length=300, unique=True, db_index=True)
    new_path = models.CharField(max_length=300)
    permanent = models.BooleanField(default=True, help_text="True for 301 Permanent, False for 302 Temporary")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SEO Redirect"
        verbose_name_plural = "SEO Redirects"
        ordering = ["old_path"]

    def __str__(self):
        code = "301" if self.permanent else "302"
        return f"[{code}] {self.old_path} -> {self.new_path}"

class SeoGlobalSettings(models.Model):
    """
    Global structured data and default search engine metadata.
    """
    default_meta_title = models.CharField(
        max_length=70,
        default="SKAD GROUP | Building Businesses. Creating Brands. Shaping the Future.",
    )
    default_meta_description = models.CharField(
        max_length=170,
        default="SKAD GROUP is a diversified corporate ecosystem building companies, brands, and platforms across international markets.",
    )
    default_og_image = models.ImageField(upload_to="seo/", blank=True)
    schema_organization_name = models.CharField(max_length=120, default="SKAD GROUP")
    schema_legal_name = models.CharField(max_length=160, blank=True)
    schema_same_as = models.JSONField(default=list, blank=True, help_text="List of official social profile URLs")

    class Meta:
        verbose_name = "SEO Global Settings"
        verbose_name_plural = "SEO Global Settings"

    def __str__(self):
        return self.default_meta_title
