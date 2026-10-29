import logging
from django.utils import timezone

try:
    from celery import shared_task
except ImportError:
    def shared_task(*dargs, **dkwargs):
        def decorator(fn):
            fn.delay = fn
            return fn
        if len(dargs) == 1 and callable(dargs[0]):
            fn = dargs[0]
            fn.delay = fn
            return fn
        return decorator

from apps.careers.models import Application

logger = logging.getLogger(__name__)

@shared_task
def prune_expired_applications():
    """
    Scheduled Celery task per Doc 1 Page 13 & 19:
    Auto-deletes job applications that have passed their legal retention date,
    safely removing private resume files from storage.
    """
    today = timezone.now().date()
    expired_apps = Application.objects.filter(retention_date__isnull=False, retention_date__lte=today)
    count = 0
    for app in expired_apps:
        try:
            if app.cv_file:
                app.cv_file.delete(save=False)
            app.delete()
            count += 1
        except Exception as e:
            logger.error(f"Error pruning application ID {app.id}: {e}")
    logger.info(f"Candidate data retention job completed: purged {count} expired applications.")
    return f"Purged {count} expired applications."

