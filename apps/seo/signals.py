import logging
from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.seo.models import Redirect
from apps.entities.models import Company, Brand, Platform
from apps.content.models import Page, Article
from apps.careers.models import Career

logger = logging.getLogger(__name__)

ROUTE_PREFIXES = {
    Company: "/companies/",
    Brand: "/brands/",
    Platform: "/platforms/",
    Page: "/",
    Article: "/insights/",
    Career: "/careers/",
}

@receiver(pre_save, sender=Company)
@receiver(pre_save, sender=Brand)
@receiver(pre_save, sender=Platform)
@receiver(pre_save, sender=Page)
@receiver(pre_save, sender=Article)
@receiver(pre_save, sender=Career)
def create_redirect_on_slug_change(sender, instance, **kwargs):
    """
    Automatically creates a 301 permanent Redirect when a published object's slug changes.
    Per page 8 of SKAD Backend Specification:
    'Signal: when a published object's slug changes, auto-create a Redirect from the old path.'
    """
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old_instance.slug != instance.slug:
        prefix = ROUTE_PREFIXES.get(sender, "/")
        old_path = f"{prefix}{old_instance.slug}" if prefix != "/" else f"/{old_instance.slug}"
        new_path = f"{prefix}{instance.slug}" if prefix != "/" else f"/{instance.slug}"

        Redirect.objects.get_or_create(
            old_path=old_path,
            defaults={"new_path": new_path, "permanent": True},
        )
        logger.info(f"Auto-created 301 Redirect: {old_path} -> {new_path}")
