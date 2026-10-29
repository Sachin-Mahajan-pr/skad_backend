import logging
from django.db import transaction
from django.db.models.signals import post_save, post_delete

from apps.entities.models import Company, Brand, Platform, Foundation
from apps.content.models import Page, Article, NewsItem, CaseStudy
from apps.careers.models import Career
from apps.taxonomy.models import Industry, Capability
from apps.core.tasks import revalidate_frontend

logger = logging.getLogger(__name__)

def compute_tags(sender, instance) -> list[str]:
    """
    Computes affected cache tags for Next.js on-demand revalidation per Page 20 of SKAD Specification.
    e.g. changing a brand invalidates brand:{slug}, brands, its company page, industries, navigation, ecosystem.
    """
    tags = ["sitemap", "navigation", "ecosystem"]
    if isinstance(instance, Company):
        tags.extend([f"company:{instance.slug}", "companies"])
    elif isinstance(instance, Brand):
        tags.extend([f"brand:{instance.slug}", "brands"])
        rel = instance.verified_company_relationship()
        if rel and rel.from_object:
            tags.append(f"company:{rel.from_object.slug}")
    elif isinstance(instance, Platform):
        tags.extend([f"platform:{instance.slug}", "platforms"])
    elif isinstance(instance, Page):
        tags.extend([f"page:{instance.slug}", "pages"])
    elif isinstance(instance, Article):
        tags.extend([f"article:{instance.slug}", "articles", "insights"])
    elif isinstance(instance, Career):
        tags.extend([f"career:{instance.slug}", "careers"])
    elif isinstance(instance, Industry):
        tags.extend([f"industry:{instance.slug}", "industries"])
    elif isinstance(instance, Capability):
        tags.extend([f"capability:{instance.slug}", "capabilities"])
    elif isinstance(instance, Foundation):
        tags.extend(["foundation", "impact"])
    return list(set(tags))

REVALIDATABLE_MODELS = (
    Company, Brand, Platform, Foundation,
    Page, Article, NewsItem, CaseStudy, Career,
    Industry, Capability
)

def on_model_change(sender, instance, **kwargs):
    tags = compute_tags(sender, instance)
    def enqueue():
        try:
            revalidate_frontend.delay(tags)
        except Exception as e:
            logger.warning("Could not enqueue revalidate_frontend: %s", e)
    transaction.on_commit(enqueue)

for model in REVALIDATABLE_MODELS:
    post_save.connect(on_model_change, sender=model)
    post_delete.connect(on_model_change, sender=model)
