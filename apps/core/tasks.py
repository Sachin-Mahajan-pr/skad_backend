import json
import hmac
import hashlib
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    from celery import shared_task
except ImportError:
    def shared_task(*args, **kwargs):
        def decorator(f):
            def delay(*a, **kw):
                return f(*a, **kw)
            f.delay = delay
            return f
        return decorator

@shared_task(bind=True, autoretry_for=(requests.RequestException,), retry_backoff=True, max_retries=6)
def revalidate_frontend(self, tags: list[str]):
    """
    Asynchronous Celery task for Next.js cache revalidation per Page 20 of SKAD Specification.
    """
    if not getattr(settings, "FRONTEND_ORIGIN", None) or not getattr(settings, "REVALIDATE_SECRET", None):
        return
    body = json.dumps({'tags': sorted(set(tags))}).encode()
    sig = hmac.new(settings.REVALIDATE_SECRET.encode(), body, hashlib.sha256).hexdigest()
    r = requests.post(
        f'{settings.FRONTEND_ORIGIN}/api/revalidate',
        data=body,
        headers={'x-skad-signature': sig, 'Content-Type': 'application/json'},
        timeout=10
    )
    r.raise_for_status()

def trigger_revalidation_sync(tags: list[str]) -> bool:
    """
    Direct synchronous revalidation call to Next.js webhook.
    Used for local testing or immediate fallback.
    """
    if not getattr(settings, "FRONTEND_ORIGIN", None) or not getattr(settings, "REVALIDATE_SECRET", None):
        return False
    
    unique_tags = sorted(list(set(tags)))
    payload = json.dumps({"tags": unique_tags}).encode("utf-8")
    signature = hmac.new(
        settings.REVALIDATE_SECRET.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()

    endpoint = f"{settings.FRONTEND_ORIGIN}/api/revalidate"
    try:
        response = requests.post(
            endpoint,
            data=payload,
            headers={
                "x-skad-signature": signature,
                "Content-Type": "application/json",
            },
            timeout=5,
        )
        return response.status_code == 200
    except Exception as e:
        logger.warning("Revalidation webhook call failed: %s", str(e))
        return False
