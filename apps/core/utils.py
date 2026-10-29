import os
import hashlib
import uuid
import nh3
from django.utils import timezone

def get_client_ip(request) -> str:
    """
    Extract verified client IP address.
    Prioritizes HTTP_X_REAL_IP set by trusted reverse proxy (Nginx) to prevent IP spoofing,
    falling back to REMOTE_ADDR.
    """
    if not request:
        return ""
    x_real_ip = request.META.get("HTTP_X_REAL_IP")
    if x_real_ip:
        return x_real_ip.strip()
    remote_addr = request.META.get("REMOTE_ADDR")
    if remote_addr:
        return remote_addr.strip()
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[-1].strip()
    return ""

def hash_ip(request) -> str:
    """
    Returns SHA-256 hash of submitter IP address for privacy compliance.
    Per page 12: 'ip_hash = models.CharField(max_length=64, blank=True) # hashed, not raw IP'
    """
    ip = get_client_ip(request)
    if not ip:
        return ""
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

def sanitize_html(html_content: str) -> str:
    """Clean rich text input using nh3 allowlist."""
    if not html_content:
        return ""
    allowed_tags = {
        "p", "b", "i", "strong", "em", "u", "h2", "h3", "h4",
        "ul", "ol", "li", "a", "blockquote", "code", "pre", "hr", "br"
    }
    allowed_attributes = {
        "a": {"href", "title", "target", "rel"}
    }
    return nh3.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)

def generate_enquiry_reference() -> str:
    """
    Generate reference ID in format SKD-YYMM-XXXX
    e.g. SKD-2610-8F3A
    """
    now = timezone.now()
    prefix = now.strftime("%y%m")
    unique_suffix = uuid.uuid4().hex[:4].upper()
    return f"SKD-{prefix}-{unique_suffix}"

def generate_preview_token(entity_type: str, slug: str) -> str:
    """
    Generate a signed, timestamped preview token for Next.js draft mode.
    Per page 9 & 10 of SKAD Backend Specification:
    'admin "Preview" button opens the Next.js draft-mode URL using a signed, short-lived token.'
    """
    from django.core.signing import TimestampSigner
    from django.conf import settings
    secret = getattr(settings, "REVALIDATE_SECRET", settings.SECRET_KEY)
    signer = TimestampSigner(key=secret, salt="skad-preview-draft-token")
    value = f"{entity_type}:{slug}"
    return signer.sign(value)

def validate_preview_token(token: str, entity_type: str = "", slug: str = "", max_age: int = 3600) -> bool:
    """
    Validates a signed preview token within the expiry window (default 1 hour).
    """
    if not token:
        return False
    from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
    from django.conf import settings
    secret = getattr(settings, "REVALIDATE_SECRET", settings.SECRET_KEY)
    signer = TimestampSigner(key=secret, salt="skad-preview-draft-token")
    try:
        unsigned = signer.unsign(token, max_age=max_age)
        if entity_type and slug:
            expected = f"{entity_type}:{slug}"
            return unsigned == expected
        return True
    except (BadSignature, SignatureExpired):
        return False


def can_access_drafts(request) -> bool:
    """
    Enforces draft protection per SKAD Spec (Doc 1, Pages 3, 9, 10).
    Drafts require either an authenticated staff session or a valid signed preview token.
    Safely handles None request during OpenAPI schema generation.
    """
    if not request:
        return False
    params = getattr(request, "query_params", getattr(request, "GET", {}))
    token = params.get("preview_token") if hasattr(params, "get") else None
    if token and validate_preview_token(token):
        return True
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated and user.is_staff)


def random_resume_upload_path(instance, filename: str) -> str:
    """Stores candidate resumes with random names in private storage per Page 13 & 19."""
    ext = os.path.splitext(filename)[1].lower()
    return f"private/resumes/{uuid.uuid4().hex}{ext}"


def random_enquiry_upload_path(instance, filename: str) -> str:
    """Stores enquiry attachments with random names in private storage per Page 13 & 19."""
    ext = os.path.splitext(filename)[1].lower()
    return f"private/enquiries/{uuid.uuid4().hex}{ext}"


def random_opportunity_upload_path(instance, filename: str) -> str:
    """Stores business opportunity attachments with random names in private storage."""
    ext = os.path.splitext(filename)[1].lower()
    return f"private/opportunities/{uuid.uuid4().hex}{ext}"


def random_document_upload_path(instance, filename: str) -> str:
    """Stores corporate documents with random names in private bucket per Page 8 & 19."""
    ext = os.path.splitext(filename)[1].lower()
    return f"documents/{uuid.uuid4().hex}{ext}"

