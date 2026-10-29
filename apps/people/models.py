from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import Publishable, PublishStatus

class PersonGroup(models.TextChoices):
    LEADERSHIP = "leadership", "Leadership"
    MANAGEMENT = "management", "Management"
    BUSINESS_HEAD = "business_head", "Business Head"
    TECHNOLOGY = "technology", "Technology"
    CREATIVE = "creative", "Creative"
    OPERATIONS = "operations", "Operations"
    ADVISOR = "advisor", "Advisor"
    STRATEGIC_EXPERT = "strategic_expert", "Strategic Expert"

class Person(Publishable):
    """
    Leadership, executive directors, and verified team members.
    Per page 7: No invented biographies. Every person needs approved name, title,
    biography, expertise, and explicit recorded consent before publishing.
    """
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    title = models.CharField(max_length=140, help_text="e.g. Founder & Group CEO, Head of Technology")
    group = models.CharField(max_length=24, choices=PersonGroup.choices, default=PersonGroup.LEADERSHIP)
    bio = models.TextField()
    photo = models.ImageField(upload_to="people/", blank=True)
    expertise = models.JSONField(default=list, blank=True, help_text="List of core competency tags")
    linkedin_url = models.URLField(blank=True)
    company = models.ForeignKey(
        "entities.Company",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_members",
    )
    consent_recorded = models.BooleanField(
        default=False,
        help_text="Mandatory personal data consent recorded before publishing publicly.",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} - {self.title}"

    def clean(self):
        super().clean()
        if self.status == PublishStatus.PUBLISHED and not self.consent_recorded:
            raise ValidationError(
                {"consent_recorded": "Cannot publish a person's profile without recorded consent."}
            )

class PersonRole(models.Model):
    """
    Explicit entity roles for a person across the SKAD ecosystem.
    e.g. Managing Director at SKAD Jewels India, Head of Strategy at CommerceOS.
    Per page 4: Located in people app.
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="roles")
    company = models.ForeignKey(
        "entities.Company",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="person_roles",
    )
    brand = models.ForeignKey(
        "entities.Brand",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="person_roles",
    )
    role_title = models.CharField(max_length=140)
    start_date = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Person Role"
        verbose_name_plural = "Person Roles"
        ordering = ["-is_primary", "person__name"]

    def __str__(self):
        target = self.company.name if self.company else (self.brand.name if self.brand else "Group")
        return f"{self.person.name} - {self.role_title} ({target})"
