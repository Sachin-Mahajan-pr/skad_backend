from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from apps.core.models import Entity, Publishable

class Group(Entity):
    """
    SKAD GROUP: Canonical ecosystem overarching identity.
    Distinct from Companies, Brands, Platforms, and Foundations.
    """
    primary_line = models.CharField(
        max_length=200,
        default="BUILDING BUSINESSES. CREATING BRANDS. SHAPING THE FUTURE.",
    )
    operating_philosophy = models.CharField(
        max_length=120,
        default="BUILD • CONNECT • SCALE",
    )
    at_a_glance_facts = models.JSONField(
        default=list,
        blank=True,
        help_text="Verified group facts only. No invented metrics.",
    )

    class Meta:
        verbose_name = "SKAD Group"
        verbose_name_plural = "SKAD Group"

    def clean(self):
        super().clean()
        if "holding" in self.name.lower():
            raise ValidationError(
                "Do not describe SKAD as a 'holding company' unless legally confirmed."
            )

class Company(Entity):
    """
    Corporate Entity Layer.
    Examples:
    - SKAD JEWELS INDIA PRIVATE LIMITED
    - LUXORA GLOW ESSENTIALS PRIVATE LIMITED
    - DETARA LTD (UK / London)
    - SKAD DIATECH EXPORTS
    """
    legal_name = models.CharField(
        max_length=200,
        help_text="Exact legal entity name as registered in corporate filings.",
    )
    company_type = models.CharField(
        max_length=120,
        help_text="e.g. 'Manufacturing + Diamond Trading', 'International Trade + Commerce Infrastructure'",
    )
    sector = models.CharField(max_length=120)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=2, blank=True, help_text="ISO 3166-1 alpha-2 code")
    registered_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Confidential registration details (CIN, VAT, registered address). Private unless flagged.",
    )
    external_url = models.URLField(blank=True)
    capabilities = models.ManyToManyField("taxonomy.Capability", blank=True, related_name="companies")
    industries = models.ManyToManyField("taxonomy.Industry", blank=True, related_name="companies")
    hero_image = models.ImageField(upload_to="companies/", blank=True)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["sort_order", "name"]

    def clean(self):
        super().clean()
        if "holding" in self.name.lower() or "holding" in self.legal_name.lower():
            # Check legal rule from spec
            raise ValidationError(
                "Do not describe any SKAD company as a 'holding company' unless legally confirmed."
            )

    @property
    def verified_brands(self):
        """Returns brands operated or owned by this company with verified relationships."""
        company_ct = ContentType.objects.get_for_model(self)
        brand_ct = ContentType.objects.get_for_model(Brand)
        rel_ids = Relationship.objects.filter(
            from_type=company_ct,
            from_id=self.id,
            to_type=brand_ct,
            relationship__in=[RelationshipType.OPERATES, RelationshipType.OWNS_BRAND],
            verified=True,
        ).values_list("to_id", flat=True)
        return Brand.objects.filter(id__in=rel_ids)

class MarketScope(models.TextChoices):
    INDIA_ONLY = "india_only", "India only"
    INTERNATIONAL = "international", "International"
    REGIONAL = "regional", "Regional"
    UNSPECIFIED = "unspecified", "Unspecified"

class Brand(Entity):
    """
    Consumer / Market Identity Layer.
    Examples:
    - DETARA (Fine Diamond Jewellery & Engagement Rings)
    - LUXORA GLOW (Hair, Skin & Beauty Studio)
    - BENAVI (Fine Silver Jewellery - India only)
    - RUPAARI (Fashion / Sarees / Indian Heritage)
    - CASE SUNO (Legal Technology)
    - ZEMO (New-Gen Fashion & Custom Wear)
    """
    tagline = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=120)
    market_scope = models.CharField(
        max_length=16,
        choices=MarketScope.choices,
        default=MarketScope.UNSPECIFIED,
    )
    positioning = models.TextField(blank=True)
    target_market = models.TextField(blank=True)
    theme = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom brand design tokens: palette, display fonts, button style, hero layout.",
    )
    website_url = models.URLField(blank=True)
    logo = models.FileField(upload_to="brands/", blank=True)
    cta_label = models.CharField(
        max_length=60,
        blank=True,
        help_text="e.g. 'EXPLORE DETARA', 'CREATE YOUR ZEMO', 'VISIT BENAVI'",
    )
    capabilities = models.ManyToManyField("taxonomy.Capability", blank=True, related_name="brands")
    industries = models.ManyToManyField("taxonomy.Industry", blank=True, related_name="brands")

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        ordering = ["sort_order", "name"]

    def clean(self):
        super().clean()
        # Enforce BENAVI specific positioning rule
        if self.slug == "benavi" or "benavi" in self.name.lower():
            if self.market_scope != MarketScope.INDIA_ONLY:
                raise ValidationError(
                    {"market_scope": "BENAVI must be marked 'India only' per canonical ecosystem rules."}
                )

    def verified_company_relationship(self):
        """
        Returns the verified parent company relationship or None.
        If relationship is not verified, returns None so API falls back to neutral association.
        """
        brand_ct = ContentType.objects.get_for_model(self)
        company_ct = ContentType.objects.get_for_model(Company)
        rel = Relationship.objects.filter(
            from_type=company_ct,
            to_type=brand_ct,
            to_id=self.id,
            relationship__in=[RelationshipType.OPERATES, RelationshipType.OWNS_BRAND],
            verified=True,
        ).select_related("from_type").first()
        return rel

class Platform(Entity):
    """
    Platforms & Ventures initiative layer.
    Examples:
    - SKAD COMMERCEOS (BUILD • LAUNCH • GROW)
    - SKAD COMMERCE LAB (AI + Human Execution)
    NOTE: Intentionally NO legal-entity fields: a platform is not a company.
    """
    purpose = models.TextField(blank=True)
    tagline = models.CharField(max_length=120, blank=True, help_text="e.g. 'BUILD • LAUNCH • GROW'")
    status = models.CharField(max_length=40, blank=True, help_text="Initiative status label")
    logo = models.FileField(upload_to="platforms/", blank=True)
    cta_label = models.CharField(max_length=60, blank=True)
    capabilities = models.ManyToManyField("taxonomy.Capability", blank=True, related_name="platforms")
    industries = models.ManyToManyField("taxonomy.Industry", blank=True, related_name="platforms")

    class Meta:
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"
        ordering = ["sort_order", "name"]

class Venture(Entity):
    """
    Future Ventures & Strategic Opportunities.
    """
    venture_type = models.CharField(max_length=80)
    stage_label = models.CharField(max_length=80, blank=True)

    class Meta:
        verbose_name = "Venture"
        verbose_name_plural = "Ventures"
        ordering = ["sort_order", "name"]

class Foundation(Entity):
    """
    Impact Layer (Kalla Rudra Foundation).
    Must remain strictly isolated from commercial corporate entities.
    """
    mission = models.TextField(blank=True)
    industries = models.ManyToManyField("taxonomy.Industry", blank=True, related_name="foundations")

    class Meta:
        verbose_name = "Foundation"
        verbose_name_plural = "Foundations"
        ordering = ["sort_order", "name"]

class RelationshipType(models.TextChoices):
    OPERATES = "operates", "Company operates brand"
    OWNS_BRAND = "owns_brand", "Company owns brand"
    SITS_WITHIN = "sits_within_ecosystem", "Platform sits within company ecosystem"
    ENDORSED_BY = "endorsed_by", "Endorsed by"
    ASSOCIATED = "associated_with", "Associated with (neutral)"
    IMPACT_OF = "impact_of", "Impact initiative of group"

class Relationship(Publishable):
    """
    Explicit, typed entity relationships with verification enforcement.
    """
    from_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="+")
    from_id = models.PositiveIntegerField()
    from_object = GenericForeignKey("from_type", "from_id")

    to_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="+")
    to_id = models.PositiveIntegerField()
    to_object = GenericForeignKey("to_type", "to_id")

    relationship = models.CharField(max_length=24, choices=RelationshipType.choices)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Entity Relationship"
        verbose_name_plural = "Entity Relationships"
        unique_together = ("from_type", "from_id", "to_type", "to_id", "relationship")

    def __str__(self):
        return f"{self.from_object} -> {self.get_relationship_display()} -> {self.to_object}"

    def clean(self):
        super().clean()
        from_model = self.from_type.model if self.from_type else None
        to_model = self.to_type.model if self.to_type else None

        # Rule 1: A Brand cannot be linked as the parent/owner of a Company
        if from_model == "brand" and to_model == "company":
            raise ValidationError("A Brand cannot be the parent or operator of a Company.")

        # Rule 2: A Platform cannot be given owns_brand
        if from_model == "platform" and self.relationship == RelationshipType.OWNS_BRAND:
            raise ValidationError("A Platform is not a legal company and cannot own a Brand.")

        # Rule 3: A Foundation cannot be related to a commercial brand as owner
        if from_model == "foundation" and self.relationship in (RelationshipType.OWNS_BRAND, RelationshipType.OPERATES):
            raise ValidationError("A Foundation cannot operate or own a commercial Brand.")

        # Rule 4: sits_within_ecosystem is only valid Platform -> Company
        if self.relationship == RelationshipType.SITS_WITHIN:
            if not (from_model == "platform" and to_model == "company"):
                raise ValidationError("'sits_within_ecosystem' is only valid from a Platform to a Company.")
