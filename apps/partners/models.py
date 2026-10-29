from django.db import models
from apps.core.models import Publishable

class PartnerType(models.TextChoices):
    STRATEGIC = "strategic", "Strategic Partner"
    SUPPLIER = "supplier", "Supplier / Manufacturer"
    DISTRIBUTOR = "distributor", "Distributor"
    TECHNOLOGY = "technology", "Technology Partner"
    INTERNATIONAL = "international", "International Trade Partner"
    FOUNDER = "founder", "Ecosystem Founder"

class Partner(Publishable):
    """
    Verified business partners and alliances.
    """
    name = models.CharField(max_length=140)
    partner_type = models.CharField(max_length=24, choices=PartnerType.choices, default=PartnerType.STRATEGIC)
    relationship_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="partners/", blank=True)
    website_url = models.URLField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"
    
    

