import os
import re
from django.core.exceptions import ValidationError

BANNED_PHRASES = [
    r"\bworld[- ]class\b",
    r"\bleading\b",
    r"\brevolutionary\b",
    r"\bbest\b",
    r"\bnumber one\b",
    r"\bunmatched\b",
    r"\blargest\b",
    r"\bglobal leader\b",
]

PLACEHOLDER_STRINGS = [
    r"\btodo\b",
    r"\btbd\b",
    r"\bplaceholder\b",
    r"\blorem ipsum\b",
]

DEFAULT_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".webp"}
DANGEROUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".sh", ".php", ".py", ".js", ".vbs", ".msi", ".dll"}

# Enforce Pillow decompression bomb limit per Page 19
try:
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = 25_000_000
except ImportError:
    Image = None

def validate_secure_image(image_obj, max_dimension=5000):
    """
    Validates uploaded image integrity and prevents decompression bombs.
    Per page 19: 'image processing (Pillow) with decompression-bomb limits'
    """
    if not image_obj or not Image:
        return
    try:
        current_pos = image_obj.tell() if hasattr(image_obj, "tell") else 0
        img = Image.open(image_obj)
        img.verify()
        if hasattr(image_obj, "seek"):
            image_obj.seek(current_pos)
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            raise ValidationError(f"Image dimensions ({width}x{height}) exceed maximum allowed ({max_dimension}x{max_dimension}px).")
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid or corrupted image file: {e}")

def validate_no_banned_phrases(value: str):
    """
    Blocks promotional superlatives not legally verified.
    Per page 9 of the SKAD specification:
    'no banned phrases in public text (world-class, leading, revolutionary,
    best, number one, unmatched, largest, global leader) unless an Approver overrides'
    """
    if not value or not isinstance(value, str):
        return
    for pattern in BANNED_PHRASES:
        match = re.search(pattern, value, flags=re.IGNORECASE)
        if match:
            raise ValidationError(
                f"Prohibited promotional phrasing detected: '{match.group(0)}'. "
                "Per SKAD corporate policy, unsupported superlatives are not permitted."
            )

def validate_no_placeholders(value: str):
    """
    Blocks unfinished draft notes from going to published content.
    Per page 9 of SKAD specification:
    'no TODO/TBD/placeholder strings'
    """
    if not value or not isinstance(value, str):
        return
    for pattern in PLACEHOLDER_STRINGS:
        match = re.search(pattern, value, flags=re.IGNORECASE)
        if match:
            raise ValidationError(
                f"Draft placeholder detected: '{match.group(0)}'. "
                "All published content must be complete."
            )

def validate_secure_file_upload(file_obj, max_mb=10, allowed_extensions=None):
    """
    Enforces secure file upload limits, safe extensions, and blocks executables/scripts.
    Per page 12 & 13: 'size limit such as 10 MB, extension and magic-byte MIME check'
    """
    if not file_obj:
        return

    # Check file size
    max_bytes = max_mb * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(f"File size exceeds maximum permitted limit of {max_mb} MB.")

    # Check file extension
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext in DANGEROUS_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' is prohibited for security reasons.")

    allowed = allowed_extensions or DEFAULT_ALLOWED_EXTENSIONS
    if ext not in allowed:
        raise ValidationError(
            f"Unsupported file extension '{ext}'. Permitted extensions: {', '.join(sorted(allowed))}"
        )

    # Magic-byte MIME signature verification per Page 13 & 19
    try:
        current_pos = file_obj.tell() if hasattr(file_obj, "tell") else 0
        header = file_obj.read(8)
        if hasattr(file_obj, "seek"):
            file_obj.seek(current_pos)

        if ext == ".pdf" and not header.startswith(b"%PDF"):
            raise ValidationError("File content does not match genuine PDF format signature.")
        elif ext == ".png" and not header.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValidationError("File content does not match genuine PNG format signature.")
        elif ext in (".jpg", ".jpeg") and not header.startswith(b"\xff\xd8\xff"):
            raise ValidationError("File content does not match genuine JPEG format signature.")
        elif ext == ".docx" and not header.startswith(b"PK\x03\x04"):
            raise ValidationError("File content does not match genuine DOCX format signature.")
        elif ext == ".doc" and not header.startswith(b"\xd0\xcf\x11\xe0"):
            raise ValidationError("File content does not match genuine DOC format signature.")
    except ValidationError:
        raise
    except Exception:
        pass

